import React from 'react';

import { Column, Table } from 'react-virtualized';
import 'react-virtualized/styles.css'; 

export default class Incident_Table extends React.PureComponent {
    constructor(probs){
	super(probs)
	this.state = {
	    incident_list: [{
		id: 1,
		time: 1,
		score: 0.5
	    }]
	}
    }
    updateTable = (time, score) => {
	console.log("update Table")
	var new_id = this.state.incident_list[this.state.incident_list.length - 1]["id"] + 1
	this.state.incident_list.push({id: new_id, time: time, score: score})
	console.log(this.state.incident_list)
	this.tableRef.forceUpdateGrid()
    }

    render() {
	return (
		<Table
		    ref={(ref) => this.tableRef = ref}
		    width={300}
		    height={300}
		    headerHeight={20}
		    rowHeight={30}
		    rowCount={this.state.incident_list.length}
		    rowGetter={({ index }) => this.state.incident_list[index]}
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
	);
    }
}
