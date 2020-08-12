import React from "react";
import Popup from "reactjs-popup";
import TextFileReader from './TextFileReader'
import './css/Popup.css'
import './css/UserActionInput.css'

//var myTxt = require("window_12:01:14Alarm_No_0");

export default class ControlledPopup extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
        open: false,
        current_alarm_file: null
    };
    this.openModal = this.openModal.bind(this);
    this.closeModal = this.closeModal.bind(this);
  }
  openModal() {
    if (this.props.filename_list.length > 0){
        this.setState({ 
            open: true,
            current_alarm_file: this.props.filename_list[this.props.filename_list.length - 1]
        });
        console.log(this.props.filename_list[this.props.filename_list.length - 1])
    }
    else {
        this.setState({ 
            open: true,
            current_alarm_file: null 
        });
    }
  }
  closeModal() {
    this.setState({ open: false });
  }

  render() {
    return (
      <div className="modal">
        <button className="button-basic" onClick={this.openModal}>
            Show tracked window of alarm
        </button>
        <Popup className="Popup"
          open={this.state.open}
          closeOnDocumentClick
          onClose={this.closeModal}
        >
          <div className="modal">
            <a className="close" onClick={this.closeModal}>
              &times;
            </a>
            <div>
                <TextFileReader
                    txt={""}
                />
            </div>
          </div>
        </Popup>
      </div>
    );
  }
}

