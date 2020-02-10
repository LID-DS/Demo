import React from 'react';
import logo from './logo.svg';
import './App.css';
import rethinkdb from 'rethinkdb'

class App extends React.PureComponent{
    constructor(){
	super()
	this.state = {
	    sum : 0
	}
    }
    render(){
	return(
		<div>{this.state.sum}</div>
	)
    }
    componentDidMount(){
	// create listener
	rethinkdb.connect({host: 'http://localhost', port: 28015}, function(err, conn) {
	    if (err) throw err
	    rethinkdb.table('statistics').changes().run(conn, function(err, cursor) {
		    if (err) throw err
		    cursor.each(function(err, row) {
			if (err) throw err
			console.log(JSON.stringify(row, null, 2))
		    })
	    })
	})
    }
}


export default App;
