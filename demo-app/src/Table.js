import React from 'react';
import { List, Column, Table, defaultTableRowRenderer } from 'react-virtualized';
import 'react-virtualized/styles.css';

export default class Incident_Table extends React.PureComponent {
    constructor(probs){
        super(probs)
        this.state = {
            incident_list:[{
                id: 0,
                time:0,
                score:0
            }],
        }
    }
    updateTable = (time, score) => {
        console.log("updateTable")
        var current_list = this.state.incident_list
        var new_id = current_list[this.state.incident_list.length - 1]["id"] + 1
        current_list.push({id: new_id, time: time, score: score})
        var list = this.state.students
        this.setState((prevState, props) => {
            return {
                incident_list: [...prevState.incident_list]
            }
        })
        console.log(current_list)
    }

    render() {
	return (
        <div>
		<Table
		    ref={(ref) => this.tableRef = ref}
		    width={300}
		    height={300}
		    headerHeight={20}
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
