import React from 'react';
import './css/TrainingInfo.css' 

import { Line } from 'rc-progress';

export default class Training_info extends React.PureComponent {

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
        
    // Invoked from IDSPlot
        var ids_state = "Training ongoing"
        if (ids_info['state'] !== 0){
            ids_state = "Detecting"
        }

        var progress = ids_info['current_ngrams']/ids_info['training_size']*100       
        this.setState({
            ids_info: {
                state_string : ids_state,
                state : ids_info['state'],
                training_size : ids_info['training_size'],
                current_ngrams : ids_info['current_ngrams'],
                progress: progress,
            }
        })
    }

    render(){
        return(
            <div className="detecting">
                <Info ids_info={this.state.ids_info}/>
                <em>Current training size: {this.state.ids_info.training_size}</em>
            </div>
        )
    }
}

function Info(probs) {
    var ids_info = probs.ids_info    
    var percentage = Math.round((ids_info.current_ngrams/ids_info.training_size) * 100)
    if (ids_info.state === 1) {
        return <div> {ids_info.state_string} </div>
    } 
    else{
        return (
            <div className="in-training">      
                <div className="training-string"> {ids_info.state_string} </div>
                <Line percent={ids_info.progress} 
                    strokeWidth="1" 
                    strokeColor="#282828"
                    trailColor="#caceca"
                    trailwidth = "1"
                    />
                <div>{percentage}%</div> 
            </div>
        )
    }
}

