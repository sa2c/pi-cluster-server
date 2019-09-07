function MainPanel(props) {
  return (
    <img id="result-main-image" src="simulations/1/elmeroutput0001-velomagn.png" alt="Image 1" width="100%" />
  );
}

function SimulationList(props) {
  return (
    props.simulations.map((sim_id, rank) => {
      const image_url = "simulations/" + sim_id +
        "/elmeroutput0001-velomagn.png"
      const image_alt = "Simulation " + sim_id + " image"
      return (
        <div className="columns simulation"
                     key={rank}
                     id="rank-{i + 1}"
                     onClick={ () => props.onClick(sim_id) }>

                  <div className="ranking column is-one-fifth">
                    <h2>
                      { rank + 1 }
                    </h2>
                  </div>

                  <div className="simulation-data">

                    <img src={image_url}
                         alt={image_alt}
                         width="100%" />

                    <div className="simulation-info">
                      <p>Mark</p>
                      <p>Drag: 1.3354</p>
                    </div>
                  </div>
                </div>
      )
    })
  );
}

class Layout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bestSimulations: [1, 3, 2, 1],
      currentSimulation: 1
    };
  }

  simulationChoiceHandler(sim_id) {
    alert('selected ' + sim_id);
  }

  render() {
    return (
      <div className="container">
              <div className="columns">
                <div className="column is-three-quarters is-vertical-centre">
                  <MainPanel/>
                </div>
                <div id="leaderboard" className="column is-scroll">
                  <SimulationList simulations={ this.state.bestSimulations }
                                  onClick={ this.simulationChoiceHandler }/>
                </div>
              </div>
            </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root')
);
