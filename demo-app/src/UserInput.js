import React from 'react';
const UserInput = probs => {
    return(
        <div className="user-input">
            <form> 
                {"Training size:    "}
                <input 
                    type="text" 
                    name="training_size"
                    ref={probs.inputRef} 
                />
            </form>
        </div>
    );
};
export default UserInput;
