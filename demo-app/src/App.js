import React from 'react';
import io from 'socket.io-client';
import './css/App.css';

import IDSPlot from './IDSPlot';
import TrainingInfo from './TrainingInfo';



class App extends React.PureComponent{

    constructor(props){
	super(props)
	this.state = {
	    websocket:0,
	    data:[]
	}
	this.idsPlot = React.createRef();
    this.trainingInfo = React.createRef();
    };

    render() {
        return(
            <div className="App">
              <header className="App-header">
                <IDSPlot ref={this.idsPlot}/>
                <TrainingInfo ref={this.trainingInfo}/>
                <div id="container"> </div>
              </header>
            </div>
        );
    };

    componentDidMount(){
        //document.body.style.backgroundColor = '#ACB2B9'
        let socket = io('ws://localhost:5000/');
        socket.on('connect', function() {
            console.log('connected')
            this.setState({
            websocket: socket
            });
        }.bind(this));

        //if recieved message stats update plot
        socket.on('stats', function(data) {
            this.setState({
                data : data
            });
            this.idsPlot.current.updatePlot(data)
            this.trainingInfo.current.update_training_info(data['ids_info'])
        }.bind(this));
    }
}

export default App;

