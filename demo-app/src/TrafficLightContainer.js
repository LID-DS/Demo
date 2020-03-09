import React from 'react';
import TrafficLight from 'react-trafficlight';

class TrafficLightContainer extends React.PureComponent {
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
	<TrafficLight
	    RedOn={this.state.redOn}
	    YellowOn={this.state.yellowOn}
	    GreenOn={this.state.greenOn}
	/>
	);
    }
}

export default TrafficLightContainer;
