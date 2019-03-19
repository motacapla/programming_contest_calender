<template>
<dir>
  hogehoge
  <h1> {{ date }} </h1>
  <h2> {{ name }} </h2>
</dir>
</template>

<script>
/* eslint-disable */
import db from './firebaseInit'

export default {
  name: 'Contests',
  data () {
    return {
      name: '',
      date: ''
    }
  },
  methods: {
    getData: function () {
      const accessPath = db.collection('contests').doc("id1")
    .onSnapshot(function(doc) {
        console.log("Current data: ", doc.data());
    });
      /*
      accessPath.on('value', (snapshot) => {
        console.log(snapshot)
        if(snapshot.exists()) {
          let snapshotValue = snapshot.val()
          console.log(snapshotValue)
          if (snapshotValue) {
	    console.log("hoge")
            this.name = snapshotValue.name
            this.date = snapshotValue.date
          } else {
	    console.log("error")
          }		
	  console.log("done")
        }
      })
      */
    }
  },  
  created: function () {
    this.getData()
  }
}
</script>

<style>
</style>
