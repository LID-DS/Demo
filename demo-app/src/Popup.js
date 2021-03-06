import React from "react";
import Popup from "reactjs-popup";
import './css/Popup.css'
import './css/UserActionInput.css'


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
    this.setState({ 
        open: true,
    });
  }

  closeModal() {
    this.setState({ open: false });
    this.props.close_popup()
  }

  componentDidMount(){
    this.setState({
        current_alarm_file: this.props.content["content"],
    })
    this.openModal()
  }

  renderTableData() {
      var ngrams = this.state.current_alarm_file.split('\n')
      return ngrams.map((ngrams) => {
         const { id, ngram } = ngrams //destructuring
         return (
            <tr key={id}>
               <td>{ngram}</td>
            </tr>
         )
      })
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
                {this.state.current_alarm_file.split("\n").map((i, key) => {
                    return <div key={key}>{i}</div>
                })}
            </div>
          </div>
        </Popup>
      </div>
    );
  }
}

