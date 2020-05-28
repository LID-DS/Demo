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
                    <div>
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
                    <button className="button-basic" 
                        onClick={this.handleSQLInjection}>
                        SQL Injection
                    </button>
                    <button className="button-basic" 
                        onClick={this.handleTryHardAttack}>
                        Try Hard SQL Injection
                    </button>
                    <button className="button-basic" 
                        onClick={this.handleFalseJWTLogin}>
                        Non Existing User Login
                    </button>
                    <button className="button-basic" 
                        onClick={this.handleXSSAttack}>
                        Simple Xss
                    </button>
                    <button 
                        className="button-basic" 
                        onClick={this.handleAdvancedXSSAttack}>
                        Advanced Xss
                    </button>
                </div>
            </div>
        );
    }
};

function EnumStatus(props) {
    console.log(props.is_running)
    if (props.is_runnning){
        return <div>Enumeration running</div>
    }
    else {
        return <div>Not running</div>
    }
}

export default UserActionInput;
