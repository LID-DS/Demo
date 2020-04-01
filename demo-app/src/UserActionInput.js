import React from 'react';
import './css/UserActionInput.css';
class UserActionInput extends React.PureComponent {
    constructor(props) {
        super(props)
        this.state = {
        }
        this.App = React.createRef();
    };
    
    handleAddUser = () => {
        this.props.onChildClick('add')
    } 
    handleRemoveUser = () => {
        this.props.onChildClick('remove')
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
            </div>
        );
    }
};
export default UserActionInput;
