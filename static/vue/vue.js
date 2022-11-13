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
        drop: e =>{
            var card_id  = e.dataTransfer.getData('card_id');
            var card = document.getElementById(card_id);
            
            card.style.display="block";

            e.target.appendChild(card);

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

            f.dataTransfer.setData('card_id',target.id);
        }
    }
});

var app = new Vue({
    el:"#app",
    delimiters:['${', '}'],
    data: function() {
        return {msg:"hello world"}
    }
});