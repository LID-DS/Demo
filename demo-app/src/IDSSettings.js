import React from 'react';
import UserInput from './UserInput'

import './css/radioButton.css'

export default class IDSSettings extends React.PureComponent{

    constructor(props){
        super(props)
        this.state = {
            chosenIDS: "Stide"
        }
        this.onChangeValue = this.onChangeValue.bind(this);
    }

    onChangeValue = event => {
        this.setState({
            chosenIDS : event.target.value 
        })
    }

    handleSaveModel = () => {
        this.props.onChildClick('save', this.state.chosenIDS)
    }

    handleLoadModel = () => {
        this.props.onChildClick('load', this.state.chosenIDS)
    }

    handleStopModel = () => {
        this.props.onChildClick('stop', this.state.chosenIDS)
    }

    handleRetrain = event => {
        if (!isNaN(this.inputElement.value)){
            this.props.onChildClick(
                'retrain', 
                this.state.chosenIDS,
                parseInt(this.inputElement.value, 10))
        }
    }

    render(){
        return(
            <div>
                <div onChange={this.onChangeValue}>
                    <label className="container">Stide
                        <input 
                            type="radio" value="Stide" 
                            name="ids" defaultChecked
                        /> 
                        <span className="radio-button">
                        </span>
                    </label>
                    <label className="container">MLP
                        <input 
                            type="radio" value="MLP" 
                            name="ids" 
                        /> 
                        <span className="radio-button">
                        </span>
                    </label>
                </div>
                <UserInput className="training-input"
                    inputRef={el => (this.inputElement = el)} 
                    onChildClick={this.handleIDSSetting}
                />
                <div>
                    <div>
                        <button className="button-basic" 
                            onClick={this.handleRetrain}>
                            Retrain IDS-Model
                        </button>
                        <button className="button-basic" 
                            onClick={this.handleSaveModel}>
                            Save Trained IDS-Model
                        </button>
                    </div>
                    <div>
                        <button className="button-basic"
                            onClick={this.handleStopModel}>
                            Stop Model
                        </button>
                        <button className="button-basic" 
                            onClick={this.handleLoadModel}>
                            Load Trained IDS-Model
                        </button>
                    </div>
                </div>
            </div>
        );
    }
};
