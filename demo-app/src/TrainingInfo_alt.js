import React from 'react';
import './css/TrainingInfo.css' 

import { Line } from 'rc-progress';

export default class Training_info extends React.PureComponent {

    constructor(props){
        super(props)
        this.state = {
            type: "",
            ids_info: {
                state_string: "",
                state: 0,
                training_size: 1,
                current_ngrams: 1,
                progress: 0
            },
            stide_active: true,
            mlp_active: false,
            training_size_input: 100000
        }
        this.handleMlpChange = this.handleMlpChange.bind(this);
        this.handleStideChange = this.handleStideChange.bind(this);
        this.saveChosenIDS = this.saveChosenIDS.bind(this);
    }
    
    update_training_info = (type, state, current_ngrams, training_size) => {
        
        if (type === 'stide'){
            this.setState({
                type: "stide",
                stide_active : true
            }) 
            //ids_info = ids_info['stide']
            // Invoked from IDSPlot
            var ids_state = "Training ongoing"
            if (state !== 0){
                ids_state = "Detecting"
            }
            var progress = current_ngrams/training_size*100       
            this.setState({
                ids_info: {
                    type : type,
                    state_string : ids_state,
                    state : state,
                    training_size : training_size,
                    current_ngrams : current_ngrams,
                    progress: progress
                }
            })
        }
        else {
           this.setState({
               type: "MLP",
               mlp_active : true,
               ids_info: {
                   type: type,
                   state : state
               }
           }) 
        }
    }

    handleStideChange = () => {
        this.setState({
            stide_active: !this.state.stide_active,
        })
        // why inverted????
    }

    handleMlpChange = () => {
        this.setState({
            mlp_active: !this.state.mlp_active,
        })
        // why inverted????
    }

    saveChosenIDS = () => {
        this.props.onChildClick([this.state.stide_active, this.state.mlp_active] )
    }

    render(){
        return(
            <div className="detecting">
                <div>{this.state.type}</div>
                <Info ids_info={this.state.ids_info}/>
                <form>
                    <label className="ids_chooser">
                        Stide Algorithm
                        <input type="checkbox" 
                            defaultChecked={this.state.stide_active} 
                            onChange={this.handleStideChange}
                        />
                        <span className="checkmark"></span>
                    </label>
                    <label className="ids_chooser">
                        MLP Algorithm
                        <input type="checkbox" 
                            defaultChecked={this.state.mlp_active} 
                            onChange={this.handleMlpChange}
                        />
                        <span className="checkmark"></span>
                    </label>
                </form>
                <button 
                    className="button-basic"
                    onClick={this.saveChosenIDS}> 
                    Confirm 
                </button>
            </div>
        )
    }
}

function Info(probs) {
    var ids_info = probs.ids_info    
    console.log(ids_info.type === "stide")

    if (ids_info.state === 1) {
        return <div> {ids_info.state_string} </div>
    } 
    else if (ids_info.state === 0 && ids_info.type === "stide"){
        var percentage = Math.round((ids_info.current_ngrams/ids_info.training_size) * 100)
        return (
            <div className="in-training">      
                <div className="training-string"> {ids_info.state_string} </div>
                <em>Current training size: {ids_info.training_size}</em>
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
    else {
        return (
            <div> else </div>
        )
    }
}

