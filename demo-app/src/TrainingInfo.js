import React from 'react';

import { Line } from 'rc-progress';

export default class Training_info extends React.PureComponent{

    constructor(props){
        super(props)
        this.state = {
            ids_info: {
                state_string: "",
                state: 0,
                training_size: 1,
                current_ngrams: 1,
                progress: 0
            },
            training_size_input: 100000
        }
    }
    
    update_training_info = (ids_info) => {

        var ids_state = "Training ongoing"
        if (ids_info['state'] !== 0){
            var ids_state = "Detecting"
        }

        var progress = ids_info['current_ngrams']/ids_info['training_size']*100       
        this.setState({
            ids_info: {
                state_string : ids_state,
                state : ids_info['state'],
                training_size : ids_info['training_size'],
                current_ngrams : ids_info['current_ngrams'],
                progress: progress
            }
        })
    }
    retrain = () => {
        console.log("Train IDS")
        //pass information to demo_stide 
    }

    set_training_size = (event) => {
        console.log(event.target.value)
        this.setState({
            training_size_input: event.target.value 
        })
        //pass information to demo_stide 
    } 
    
    start_training = () => {
        console.log("start training")
        //pass infrmation to demo_stide
    }
    
    render(){
        return(
            <div>
                <Info ids_info={this.state.ids_info}/>
                <form>
                    Training size: 
                    <input 
                        type="text" 
                        name="training_size"
                        value={this.state.training_size_input}
                        onChange={this.set_training_size}
                    />
                </form>
                <button onClick={() => this.retrain()}>Train IDS</button>
            </div>
        )
    }
}
function Info(probs) {
    var ids_info = probs.ids_info    
    console.log(probs.ids_info)
    if (ids_info.state === 1) {
        return <div> {ids_info.state_string} </div>
    } 
    else{
        return (
            <div>      
                <div> {ids_info.state_string} </div>
                <Line percent={ids_info.progress} strokeWidth="4" strokeColor="#236845" />
                <div> {ids_info.current_ngrams - 1} von {ids_info.training_size}</div> 
            </div>
        )
    }
}

