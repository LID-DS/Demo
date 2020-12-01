import React from 'react';
import './css/Table.css'
import Popup from './Popup'

export default class Incident_Table extends React.PureComponent {

    constructor(props){
        super(props)
        this.state = {
            incident_list:[{
                id: null,
                time:null,
                score:null,
                ids_type:null,
                content:null
            }],
            file_list: [],
            open_popup:false,
            selected_incident:0
        }
    }

    add_incident = (time, score, content, ids_type) => {
        var current_list = this.state.incident_list
        var new_id = current_list[this.state.incident_list.length - 1]["id"] + 1
        current_list.push({
            id: new_id, 
            time: time, 
            score: score,
            ids_type: ids_type,
            content: content
        })
        this.setState({
            file_list: current_list
        })
        this.setState((prevState, props) => {
            return {
                incident_list: [...prevState.incident_list]
            }
        })
    }
    
    setIncidentForPopup = (id) => {
        this.setState({
            open_popup:true,
            selected_incident:id 
        })
    }

    closeIncidentPopup = () => {
        this.setState({
            open_popup:false
        })
    }

    renderTableData() {
      return this.state.incident_list.map((incident, index) => {
         const { id, time, score, type } = incident //destructuring
         return (
            <tr key={id} onClick={() => this.setIncidentForPopup(id)}>
               <td>{id}</td>
               <td>{time}</td>
               <td>{score}</td>
               <td>{type}</td>
            </tr>
         )
      })
    }

    renderTableHeader() {
        let header = Object.keys(this.state.incident_list[0])
        return header.map((key, index) => {
            return <th key={index}>{key.toUpperCase()}</th>
        })
    }
        

   render() {
      return (
        <div>
            <div className='table-container'>
                <h1 className='title'>Incidents</h1>
                <table className='incident'>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>TIME</th>
                            <th>SCORE</th>
                            <th>TYPE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.renderTableData()}
                    </tbody>
                </table>
        </div>
        <div>
          <ShowPopup popup={this.state.open_popup} file={this.state.file_list[this.state.selected_incident]} close={this.closeIncidentPopup}/>
        </div>
          </div>
      )
   }
}

function ShowPopup(props){
    if (props.popup) {
        return (
            <div>
                <Popup content={props.file} close_popup={props.close}/>
            </div>
        )
    } 
    else {
        return (
            <div>
            </div>
        )
    }
}

