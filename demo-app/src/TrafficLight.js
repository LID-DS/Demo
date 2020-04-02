import React from 'react';
import ReactTrafficLight from 'react-trafficlight';

import './css/TrafficLight.css'
class TrafficLight extends React.PureComponent {
    state = {
	redOn: true,
	yellowOn: false,
	greenOn: false,
    }

    updateLight = (state) => {
	this.setState({
	    redOn: state[0],
	    yellowOn: state[1],
	    greenOn: state[2]
	});
    }

    render() {
	return (
	<ReactTrafficLight className="traffic-light"
	    RedOn={this.state.redOn}
	    YellowOn={this.state.yellowOn}
	    GreenOn={this.state.greenOn}
	/>
	);
    }
}

export default TrafficLight;
