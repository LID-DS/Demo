import React from 'react';
import { Column, Table } from 'react-virtualized';
import 'react-virtualized/styles.css';
import './css/Table.css'

export default class Incident_Table extends React.PureComponent {

    constructor(props){
        super(props)
        this.state = {
            incident_list:[{
                id: 0,
                time:0,
                score:0
            }],
        }
    }

    add_incident = (time, score) => {
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
		<Table
		    ref={(ref) => this.tableRef = ref}
		    width={300}
		    height={300}
		    headerHeight={40}
		    rowHeight={30}
		    rowCount={this.state.incident_list.length}
		    rowGetter={({ index }) => this.state.incident_list[index]}
            isScrolling={true}
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
	);
    }
}
