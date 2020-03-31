import React from 'react';
const UserInput = probs => {
    return(
        <div>
            <form> 
                Training size: 
                <input 
                    type="text" 
                    name="training_size"
                    value="100000"
                    ref={probs.inputRef} 
                />
            </form>
        </div>
    );
};
export default UserInput;
