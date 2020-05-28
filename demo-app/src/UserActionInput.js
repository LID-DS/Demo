import React from 'react';
import './css/UserActionInput.css';
class UserActionInput extends React.PureComponent {
    constructor(props) {
        super(props)
        this.state = {
            userCount: 0,
            training_running: false,
            removingUser: false
        }
        this.App = React.createRef();
    };
    
    handleAddUser = () => {
        this.props.onChildClick('add')
    } 
    
    handleAddUserHead = () => {
        this.props.onChildClick('add_head')
    } 

    handleRemoveUser = () => {
        this.props.onChildClick('remove')
        this.setState({removingUser: true})
    } 

    handleStartTraining = () => {
        this.props.onChildClick('start_training')
    }

    handleStopTraining = () => {
        this.props.onChildClick('stop_training')
    }

    updateCount = (userAction) => {
        if (userAction != null){
            let userCount = userAction['userCount']
            let training_running = userAction['training_running']
            this.setState({
                userCount: userCount,
                training_running: training_running,
                removingUser: false 
            }) 
        }
    }

    render() {
        return(
            <div className="user-action-input">
                Automated User Actions 
                    
                <div className="button-container">
                    <button 
                        className="button-basic" 
                        onClick={this.handleAddUser}
                    >
                        Add User
                    </button>
                    <button 
                        className="button-basic"
                        onClick={this.handleAddUserHead}
                    >
                        Add Visible User
                    </button>
                    <button 
                        className="button-basic"
                        onClick={this.handleRemoveUser}
                    >
                        Remove User
                    </button>
                    <button 
                        className="button-basic"
                        onClick={this.handleStartTraining}
                    >
                        Start Training Sequence 
                    </button>
                    <button 
                        className="button-basic"
                        onClick={this.handleStopTraining}
                    >
                        Stop Training Sequence 
                    </button>
                </div>
                <div>
                    <TrainingInfo 
                        userInfo={this.state.training_running}/>
                </div>
                <div> 
                        <Info userInfo={this.state}/>
                </div>
            </div>
        );
    }
};

function TrainingInfo(probs) {
    if (probs.userInfo === true) {
        return (<div>Training Sequence Running</div>)
    }
    else {
        return null 
    }
}

function Info(probs) {
    if (probs.userInfo.removingUser) {
        return (
            <div>
                <div className="active-user">Active users: {probs.userInfo.userCount}</div>
                <div className="user-logout">
                    <span syle="color: #FF0000">Waiting for user to log out.</span>  
                </div>
            </div>
        )
    }
    if (probs.userInfo.userCount === 0) {
        return <span syle="background-color: #FFFF00">No running users.</span>  
    }
    if (probs.userInfo.userCount > 0) {
        return <div className="active-user">Active users: {probs.userInfo.userCount}</div>
    }
}

export default UserActionInput;
