import React from 'react';
import { Column, Table } from 'react-virtualized';
import 'react-virtualized/styles.css';
import './css/Table.css'
import Popup from './Popup'

export default class Incident_Table extends React.PureComponent {

    constructor(props){
        super(props)
        this.state = {
            incident_list:[{
                id: null,
                time:null,
                score:null
            }],
            filename_list: [] 
        }
    }

    add_incident = (time, score, filename_list) => {
        this.setState({
            filename_list: filename_list
        })
        var current_list = this.state.incident_list
        var new_id = current_list[this.state.incident_list.length - 1]["id"] + 1
        current_list.push({id: new_id, time: time, score: score})
        this.setState((prevState, props) => {
            return {
                incident_list: [...prevState.incident_list]
            }
        })
    }


    render() {
	return (
        <div>
            <div>
                <Table
                    ref={(ref) => this.tableRef = ref}
                    width={400}
                    height={400}
                    headerHeight={40}
                    rowHeight={30}
                    rowCount={this.state.incident_list.length}
                    rowGetter={({ index }) => this.state.incident_list[index]}
                    isScrolling={true}
                    onRowClick={({index}) => { console.log("click row") }}
                    onRowDoubleClick={({index}) => { console.log("click row double") }}
                    onRowMouseOver={({index}) => { console.log("mouse over") }}
                    onHeaderClick={({index}) => {console.log("header")}}
                    onRowRightClick={({index}) => { console.log("right click row") }}
                    onColumnClick={({index}) => { console.log("column click") }}
                    distance={10} 
                >
                    <Column
                    label='ID'
                    dataKey='id'
                    width={100}
                    />
                    <Column
                    width={100}
                    label='Time'
                    dataKey='time'
                    />
                    <Column
                    width={100}
                    label='Score'
                    dataKey='score'
                    />
                </Table>
            </div>
            <div>
                <Popup filename_list={this.state.filename_list}/>
            </div>
        </div>
	);
    }
}
 
