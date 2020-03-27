import React from 'react';

import { Line } from 'rc-progress';

export default class Training_info extends React.PureComponent{

    constructor(props){
        super(props)
        this.state = {
            ids_info: {
                state_string: "",
                state: 0,
                training_size: 0,
                current_ngrams: 0,
                progress: 0
            },
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


    
    render(){
    return(
        <div>
            <div> {this.state.ids_info.state_string} </div>
            <Line percent={this.state.ids_info.progress} strokeWidth="4" strokeColor="#236845" />
            <div> {this.state.ids_info.current_ngrams - 1} von {this.state.ids_info.training_size}</div> 
        </div>
    )
    }
}
