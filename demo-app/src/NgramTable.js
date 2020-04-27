import React from 'react';
import { Column, Table } from 'react-virtualized';
import 'react-virtualized/styles.css';
import './css/Table.css'

export default class Ngram_Table extends React.PureComponent {

    constructor(props){
        super(props)
        this.state = {
            ngram_list:[{
                ngram: 0,
                count: 0
            }],
            label_1: "Loading",
            label_2: "Loading",
            table_width : 400,
            column_1_width : 200,
            column_2_width : 200
        }
        this.showNgramString = this.showNgramString.bind(this)
        this.handleOverRow = this.handleOverRow.bind(this)
    }

    update_list = (raw_ngram_list) => {
        var current_list = []
        //if second argument is string, then its the convert int to sys table
        try{
            if (typeof raw_ngram_list[0][1] === 'string' || raw_ngram_list[0][1] instanceof String) {
                this.setState({
                    label_1 : "Number",
                    label_2 : "Syscall Type"
                })
            }
            else {
                this.setState({
                    label_1 : "Ngram",
                    label_2 : "Count",
                    table_width : 600,
                    column_1_width : 400
                })
            }
        }
        catch(err) {
            console.log("Wait for first ngrams") 
        }
        var i
        for (i=0; i<raw_ngram_list.length; i++){
            current_list.push({
                    ngram: raw_ngram_list[i][0], 
                    count: raw_ngram_list[i][1]
            }) 
        }
        this.setState((prevState, props) => {
            return {
                ngram_list: current_list
            }
        })
    }

    showNgramString = (event) => {
        console.log("mouse over row")
        console.log(event) 
    }
        
    handleOverRow = (event) => {
        console.log("mouse over row")
        console.log(event) 
    }

    render() {
	return (
		<Table
		    ref={(ref) => this.tableRef = ref}
		    width={this.state.table_width}
		    height={400}
		    headerHeight={40}
		    rowHeight={30}
		    rowCount={this.state.ngram_list.length}
		    rowGetter={({ index }) => this.state.ngram_list[index]}
            isScrolling={true}
            onRowClick={this.showNgramString}
            onRowMouseOver={this.handleOverRow}
            onHeaderClick={this.showNgramString}
            onColumnClick={this.showNgramString}
            onRowDoubleClick={this.handleOverRow}
		>
		    <Column
		    width={this.state.column_1_width}
		    label={this.state.label_1}
		    dataKey='ngram'
		    />
		    <Column
		    width={this.state.column_2_width}
		    label={this.state.label_2}
		    dataKey='count'
		    />
		</Table>
	);
    }
}
