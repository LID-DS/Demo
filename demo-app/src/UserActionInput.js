import React from 'react';
import './css/UserActionInput.css';
class UserActionInput extends React.PureComponent {
    constructor(props) {
        super(props)
        this.state = {
            userCount: 0,
            removingUser: false
        }
        this.App = React.createRef();
    };
    
    handleAddUser = () => {
        this.props.onChildClick('add')
    } 

    handleRemoveUser = () => {
        this.props.onChildClick('remove')
        this.setState({removingUser: true})
    } 

    updateCount = (userCount) => {
        console.log("change userCount")
        this.setState({
            userCount: userCount,
            removingUser: false 
        }) 
    }

    render() {
        return(
            <div className="UserActionInput">
                Automated User Actions 
                    
                <div className="button-container">
                    <button 
                        className="button-basic" 
                        onClick={this.handleAddUser}
                    >Add User</button>
                    <button 
                        className="button-basic"
                        onClick={this.handleRemoveUser}
                    >Remove User</button>
                </div>
                <div> 
                        <Info userInfo={this.state}/>
                </div>
            </div>
        );
    }
};

function Info(probs) {
    if (probs.userInfo.removingUser) {
        return (
                <div>
                    <span syle="color: #FF0000">Waiting for user to log out.</span>  
                    <div>Active users: {probs.userInfo.userCount}</div>
                </div>)
    }
    if (probs.userInfo.userCount === 0) {
        return <span syle="background-color: #FFFF00">No running users.</span>  
    }
    else {
        return <div>Active users: {probs.userInfo.userCount}</div>
                        
    }
}

export default UserActionInput;
