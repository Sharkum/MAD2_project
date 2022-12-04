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
        editing: [],
        edited:{},
        auth_token : null,
        interval:null
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
        last_modified(time){
            var last_modified = new Date(time);
            diff = new Date(this.present_datetime) - last_modified
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
                
            }).then(response => console.log(response))
            this.edited = {}
            return
        }
        
    },
    computed:{
        present_datetime(){
            var curr = new Date()
            return curr.getFullYear()+'-'+(curr.getMonth()<9?'0':'')+(curr.getMonth()+1)+'-'+(curr.getDate()<10?'0':'')+curr.getDate()+'T'+(curr.getHours()<10?'0':'')+curr.getHours()+':'+(curr.getMinutes()<10?'0':'')+curr.getMinutes()
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
            this.update_cards()}, 180000)
    }
});