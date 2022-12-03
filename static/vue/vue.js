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
            e.target.appendChild(card);

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
        cards_transfered:[],
        editing:[],
        edited:[]
    },
    methods:{
        card_transfer(card_id,listold,listnew){
            this.cards_transfered.push([card_id,listold,listnew])
            return
        },
        card_edit(cardid){
            this.editing.push(cardid)
            return
        },
        card_edited(cardid){
            listid = document.getElementById('card-'+cardid).parentElement.id;
            this.lists[listid].cards['card-'+cardid].Last_modified = this.present_datetime

            this.edited.push(cardid)
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
        }
    },
    computed:{
        present_datetime(){
            var curr = new Date()
            return curr.getFullYear()+'-'+(curr.getMonth()<9?'0':'')+(curr.getMonth()+1)+'-'+(curr.getDate()<10?'0':'')+curr.getDate()+'T'+(curr.getHours()<10?'0':'')+curr.getHours()+':'+(curr.getMinutes()<10?'0':'')+curr.getMinutes()
        }
    }
});