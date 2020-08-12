import React from 'react';
import './css/UserActionInput.css';

class UserActionInput extends React.PureComponent {
    constructor(props) {
        super(props)
        this.state = {
            enum_running: false
        }
    };

    handleSQLInjection = () => {
        this.props.onChildClick('start attack', 'sql')
    }

    handleTryHardAttack = () => {
        this.props.onChildClick('start attack', 'try hard sql')
    }

    handleFalseJWTLogin = () => {
        this.props.onChildClick('start attack', 'false jwt login')
    }

    handleEnum = () => {
        this.setState({
            enum_running: true
        })
        // send signal to start dirb enumeration
        this.props.onChildClick('enum', null) 
    }

    handleXSSAttack = () => {
        // start XSS Attack
        this.props.onChildClick('start attack', 'xss simple')
    }

    handleAdvancedXSSAttack = () => {
        // start advanced XSS Attack
        this.props.onChildClick('start attack', 'xss advanced')
    }

    handleSensitiveDataExposure = () => {
        this.props.onChildClick('start attack', 'data exposure simple')
    }
    
    handleSensitiveDataExposureAdvanced = () => {
        this.props.onChildClick('start attack', 'data exposure advanced')
    }

    handleRemoteCodeExecution = () => {
        this.props.onChildClick('start attack', 'remote code execution')
    }

    handleFileOverride= () => {
        this.props.onChildClick('start attack', 'file override')
    }

    updateEnum = (state) => {
        this.setState({
           enum_running: state
        })
    }

    render() {
        return(
            <div className="attack-input">
                <div className="button-container">
                    <div className="title">
                        Reconnaissance:{"\n"}
                    </div>
                    <div className="enumeration">
                        <button 
                            className="button-basic" 
                            onClick={this.handleEnum}>
                            Launch Dirb Enum
                        </button> 
                        <EnumStatus is_running={this.state.enum_running}/>
                    </div>
                    <div className="title">
                        Attacks:{"\n"}
                    </div>
                    <div className="button-container">
                        <button className="button-basic" 
                            onClick={this.handleSQLInjection}>
                            SQL Injection
                        </button>
                        <button className="button-basic" 
                            onClick={this.handleTryHardAttack}>
                            Try Hard SQL Injection
                        </button>
                    </div>
                    <div className="button-container">
                        <button className="button-basic" 
                            onClick={this.handleFalseJWTLogin}>
                            Non Existing User Login
                        </button>
                        <button className="button-basic" 
                            onClick={this.handleXSSAttack}>
                            Simple Xss
                        </button>
                        <button 
                            className="button-xss-advanced" 
                            onClick={this.handleAdvancedXSSAttack}>
                            Advanced Xss
                        </button>
                    </div>
                    <div className="button-container">
                        <button 
                            className="button-basic"
                            onClick={
                                this.handleSensitiveDataExposure}>
                            Data Exposure
                        </button>
                        <button 
                            className="button-basic"
                            onClick={
                                this.handleSensitiveDataExposureAdvanced}>
                            Data Exposure Advanced
                        </button>
                    </div>                        
                    <div className="button-container">
                        <button
                            className="button-basic"
                            onClick={
                                this.handleRemoteCodeExecution}>
                            Remote Code Execution
                        </button>
                    </div>
                    <div className="button-container">
                        <button
                            className="button-basic"
                            onClick={
                                this.handleFileOverride}>
                            File Override
                        </button>
                    </div>
                </div>
            </div>
        );
    }
};


function EnumStatus(props) {
    const is_running = props.is_running
    if (is_running){
        return <div>Enumeration running</div>
    }
    else {
        return null
    }
}

export default UserActionInput;
