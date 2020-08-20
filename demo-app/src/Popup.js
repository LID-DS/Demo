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
        current_alarm_file: ""
    };
    this.openModal = this.openModal.bind(this);
    this.closeModal = this.closeModal.bind(this);
  }

  openModal() {
    var filename = this.props.filename
    console.log(filename)
    this.setState({ 
        open: true,
        current_alarm_file: filename
    });
  }

  closeModal() {
      this.setState({ open: false });
      this.props.close_popup()
  }

  componentDidMount(){
      this.openModal()
  }

  render() {
    return (
      <div className="modal">
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
                    txt={this.state.current_alarm_file}
                />
            </div>
          </div>
        </Popup>
      </div>
    );
  }
}

