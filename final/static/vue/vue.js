Vue.component('list',{
    template:`
    <div
        :id="id"
        class="list"
        @dragover.prevent
        @drop.prevent="drop"
    >
        <slot />
    </div>`,
    props:['id'],
    methods: {
        drop(e){
            var card_id  = e.dataTransfer.getData('card_id');
            var list_id_old = e.dataTransfer.getData('list_id_old')
            var card = document.getElementById(card_id);
            
            card.style.display="block";

            var listid = e.target.id;
            this.$root.card_transfer(card_id,list_id_old,listid);
        }
    }
});

Vue.component('card',{
    template:`
    <div
        :id="id"
        class="card"
        :draggable="draggable"
        @dragstart="dragStart"
        @dragover.stop
    >
        <slot />
    </div>`,
    props:['id','draggable'],
    methods:{
        dragStart: f =>{
            var target= f.target;
            var list_old = document.getElementById(target.id).parentElement;

            f.dataTransfer.setData('card_id',target.id);
            f.dataTransfer.setData('list_id_old',list_old.id);
        }
    }
});

var app = new Vue({
    el:"#app",
    delimiters:['${', '}'],
    data: {
        lists: JSON.parse(temp),
        lists_shown: [],
        editing: [],
        edited:{},
        list_editing:[],
        list_edited:new Set(),
        auth_token : null,
        interval:null,
        metrics: JSON.parse(temp),
        reminder_time:new Date(Date.parse(new Date())+1000*60*60*24),
        reminder_message:null,
        reminder_url:null,
        remind_set:false
    },
    methods:{
        card_transfer(card_id,listold,listnew){
            let listid = this.lists[listnew].listinfo.ListID;

            this.lists[listnew].cards[card_id] = this.lists[listold].cards[card_id];
            this.lists[listnew].cards[card_id].ListID = listid;

            delete this.lists[listold].cards[card_id]

            if(!(listnew in this.edited)){
                this.edited[listnew] = new Set()
            }

            this.edited[listnew].add(card_id)
            return
        },
        card_edit(cardid){
            this.editing.push(cardid)
            return
        },
        card_edited(cardid){
            listid = document.getElementById('card-'+cardid).parentElement.id;
            this.lists[listid].cards['card-'+cardid].Last_modified = this.present_datetime

            if(!(listid in this.edited)){
                this.edited[listid] = new Set()
            }
            
            this.edited[listid].add('card-'+cardid)
            this.editing = this.editing.filter(a => a != cardid)

            return
        },
        list_edit(listid){
            this.list_editing.push(listid)
            return
        },
        lists_edited(listid){
            this.list_edited.add(listid)
            this.list_editing = this.list_editing.filter(a => a != listid)
            return
        },
        last_modified(time){
            var last_modified = new Date(time);
            var diff = new Date(this.present_datetime) - last_modified
            var seconds = diff/1000
            var minutes = seconds/60
            var hours = minutes/60
            var days = hours/24
            var weeks = days/7
            if(weeks > 1){
                return "Last modified "+Math.floor(weeks) + " weeks ago"
            }
            if(days > 1){
                return "Last modified " + Math.floor(days) + " days ago"
            }
            if(hours > 1){
                return "Last modified " + Math.floor(hours) + " hours ago"
            }
            if(minutes > 1){
                return "Last modified " + Math.floor(minutes) + " minutes ago"
            }
            return "Last modified just now"
        },
        async update_cards(){
            let body_list = {}
            var changes = 0
            for( const listid in this.edited){
                let temp = Array.from(this.edited[listid])
                for(const card in temp){
                    if(temp[card] in this.lists[listid].cards){
                    body_list[temp[card]] = this.lists[listid].cards[temp[card]]
                    }
                    changes=changes+1
                }
            }
            if(changes == 0){
                return
            }
            const response = fetch('http://127.0.0.1:5000/api/updatecards',{
                headers:{"Content-type": "application/json",
                        "Authentication-Token":this.auth_token},
                method:"POST",
                body: JSON.stringify(body_list)
                
            }).then(response => response)
            this.edited = {}
            this.editing = []
            return
        },
        async update_lists(){
            let body_list = {}
            var changes = 0
            var temp = Array.from(this.list_edited)
            for( const listid in temp){
                body_list[temp[listid]] = this.lists[temp[listid]].listinfo
                changes = changes + 1
            }
            if(changes == 0){
                return
            }
            const response = fetch('http://127.0.0.1:5000/api/updatelists',{
                headers:{"Content-type": "application/json",
                        "Authentication-Token":this.auth_token},
                method:"POST",
                body: JSON.stringify(body_list)
                
            }).then(response => response)
            this.list_edited = {}
            this.list_editing = []
            return
        },
        update_all(){
            this.update_cards();
            this.update_lists()
            return
        },
        async card_del(cardid){
            listid = document.getElementById('card-'+cardid).parentElement.id;

            document.getElementById('card-'+cardid).style.display="none";

            delete this.lists[listid].cards['card-'+cardid]
            
            const response = fetch('http://127.0.0.1:5000/api/'+cardid+'/delete',{
                headers:{"Content-type": "application/json",
                        "Authentication-Token":this.auth_token},
                method:"DELETE",
                body: {}})
            return
        },
        unset_remind(){
            this.remind_set=false;
            return
        },
        set_remind(){
            this.remind_set=true;
            localStorage.setItem('remind_time',this.reminder_time)
            localStorage.setItem('message',this.reminder_message)
            localStorage.setItem('url',this.reminder_url)
            return
        },
        send_reminder(){
            if(!this.reminder_url | !this.reminder_message){
                return
            }
            let tasks_left=0
            for(l in this.lists){
                let list = this.lists[l]
                for(c in list.cards){
                    if(!list.cards[c].Deadline){
                        tasks_left=task_left+1
                        break
                    }
                }
                if(tasks_left) break
            }
            if(tasks_left){
                var response = fetch(this.reminder_url,{method:"POST",body:JSON.stringify({'text':this.reminder_message})})
            }
            return
        },
        get_deadline(time){
            let deadline = new Date(time)
            let diff = deadline - new Date()

            var seconds = diff/1000
            var minutes = seconds/60
            var hours = minutes/60
            var days = hours/24
            var weeks = days/7
            if(weeks > 1){
                return "Due in "+Math.floor(weeks) + " weeks"
            }
            if(days > 1){
                return "Due in " + Math.floor(days) + " days"
            }
            if(hours > 1){
                return "Due in " + Math.floor(hours) + " hours"
            }
            if(minutes > 1){
                return "Due in " + Math.floor(minutes) + " minutes"
            }
            return "Deadline missed"
        },
        finish_task(cardid){
            listid = document.getElementById('card-'+cardid).parentElement.id;
            this.lists[listid].cards['card-'+cardid].Date_completed = (new Date()).toISOString()

            console.log((new Date()).toISOString())
            
            if(!(listid in this.edited)){
                this.edited[listid] = new Set()
            }

            this.edited[listid].add('card-'+cardid)
            return
        }
    },
    computed:{
        present_datetime(){
            var curr = new Date()
            return curr.getFullYear()+'-'+(curr.getMonth()<9?'0':'')+(curr.getMonth()+1)+'-'+(curr.getDate()<10?'0':'')+curr.getDate()+'T'+(curr.getHours()<10?'0':'')+curr.getHours()+':'+(curr.getMinutes()<10?'0':'')+curr.getMinutes()
        },
        remind_delay(){
            if(this.remind_set){
            var curr = new Date()
            var target = curr
            var remind_time = new Date(this.reminder_time)
            if(curr.getTime() > remind_time.getTime()){
                target = new Date(Date.parse(curr)+1000*60*60*24)
            }
            var reminding_date = new Date(target.getFullYear(),target.getMonth(),target.getDate(),
                                            remind_time.getHours(),remind_time.getMinutes(),remind_time.getSeconds())
            
            return reminding_date - curr
        }
        }
    },
    async created(){

        const loggedout = await fetch('http://127.0.0.1:5000/logout')
        let data = {
            "email":"sharan342.kumar@gmail.com",
            "password":"Wiydimam24"
        }
        const response = await fetch('http://127.0.0.1:5000/login?include_auth_token',
                            {headers:{'Content-type': 'application/json'},
                            method:"POST",
                            body: JSON.stringify(data)
                            }).then(response => response.json())
        this.auth_token = response.response.user.authentication_token;


        this.interval = setInterval(()=>{
            this.update_all()}, 180000)


        this.reminder_time=localStorage.getItem('remind_time')
        this.reminder_message=localStorage.getItem('message')
        this.reminder_url=localStorage.getItem('url')


        if(this.reminder_time){
            var timeout = setTimeout(()=>{
                this.send_reminder();
            },this.remind_delay)
        }

        for(l in this.lists){
            this.lists_shown.push(this.lists[l]['listinfo']['ListID']);
        }
    }
});