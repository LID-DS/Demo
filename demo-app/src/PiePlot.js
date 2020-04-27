import React from 'react';
import Plot from 'react-plotly.js';
import './css/Plot.css'

const pieColors = ['#9d962f','#4f767d', '#7b8d3f', '#94384c', '#7e4e7e', '#770d09', '#fe8019', '#b8bb26', '#fb4934', '#d3869b', '#83a598'] 
const highlight_color = '#f9f5d7'

class PiePlot extends React.PureComponent{
    
    constructor(props){
        super(props)
        this.state = {
            values: [],
            labels: [],
            converted_labels: [],
            hover_text: [],
            converted: false
        }
    }

    handleValues = (data) => {
        var i;
        let values = []
        let labels = []


        for (i = 0; i < data.length; i++){
            let labels_tmp = Object.keys(data[i])
            let values_tmp = Object.values(data[i])
            labels.push(labels_tmp[0])
            values.push(values_tmp[0])
        }
        this.setState({
            values: values,
            labels: labels
        })

        if(this.props.info === "ngram" && !this.state.converted && this.state.labels.length === 11){
            this.setState({
                converted_labels : this.convertLabels(this.state.labels, this.props.conversionTable['int_to_sys']),
                converted : true 
            })
            console.log(this.state.converted_labels)
        }
    }

    convertLabels = (labels, conversionTable) => {
        var i
        var string_labels = []
        for(i=0; i<labels.length; i++){
            if(labels[i] !== 'others'){
                string_labels.push(this.convertNgramToString(labels[i].split(','), conversionTable))
            }
        }
        return string_labels
    }

    convertNgramToString = (int_ngram, conversionTable) => {
        var old_ngram = int_ngram[0]    
        var string_ngram = []
        string_ngram.push(conversionTable[old_ngram - 1][1])
        var i
        for(i=1; i<int_ngram.length; i++){
            string_ngram.push(conversionTable[int_ngram[i] - 1][1])    
        }
        return string_ngram.toString()
    }

    componentDidMount(){
    }

    render(){
        return(
            <Plot
                className="dist-plot"
                data={[
                {
                    hovertext: this.state.converted_labels,
                    values: this.state.values, 
                    labels: this.state.labels,
                    type: 'pie',
                    marker: {
                        colors: pieColors 
                    },
                    hoverlabel: {
                        font: {
                            size: 18,
                            color: '#f9f5d7',
                            bordercolor:'#f9f5d7'
                        }
                    }
                }
                ]}
                layout={
                {
                    legend : {
                        font : {
                            size: 18,
                            color: highlight_color
                        }
                    },
                    datarevision: this.props.value,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)'
                }
                }
                />
        )
    }
}

export default PiePlot;
