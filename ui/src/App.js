import React from 'react';
import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Tabs from '@material-ui/core/Tabs'
import axios from 'axios'
import Tab from '@material-ui/core/Tab'
import Dialog from '@material-ui/core/Dialog'
import DialogContent from '@material-ui/core/DialogContent'
import DialogActions from '@material-ui/core/DialogActions'
import ListSubheader from '@material-ui/core/ListSubheader';
import DeleteIcon from '@material-ui/icons/Delete'
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction'
import Typography from '@material-ui/core/Typography'
import TextField from '@material-ui/core/TextField'
import ListItemText from '@material-ui/core/ListItemText'
import IconButton from '@material-ui/core/IconButton'
import Button from '@material-ui/core/Button'
import { withStyles } from '@material-ui/core/styles'
import './App.css';

const styles = theme => ({
  image: {
    width: "100%"
  },
  imageWrapper: {
    padding: "1rem"
  },
  configWrapper: {
    padding: "1rem"
  },
  deviceListWrapper: {
    padding: "1rem",
  },
  deviceItem: {
    '&:hover': {
      backgroundColor: "#d3d3d3",
      cursor: "pointer"
  }
  }
})

class App extends React.PureComponent {
  state = {
    tab: 0,
    newDevice: {
      id: "",
      name: "",
      type: ""
    },
    addingDeviceDialog: false,

    // global config
    intervalTime: "",
    outputPath: "",
    devices: [{
              id : "0",
              name : "front",
              type : "webcam"
            },
            {
              id : "1",
              name : "back",
              type : "webcam"
            },
          ],
    currentlySelectedDeviceId: "0",
  }

  handleRemoveDevice = device => _ =>  {
    console.log(device)
  }

  handleConfigSubmit = () => {
    this.setState({
      submitting: true
    })
    axios.post('http://localhost:5000/config', 
      {
        outputPath: this.state.outputPath,
        intervalTime: this.state.intervalTime,
      }
    )
    .then(response => {
      console.log(response.data)
      this.setState({
        submitting: false
      })
    })
    .catch(err => {
      console.log(err)
      this.setState({
        submitting: false
      })
    })
  }

  handleAddDevice = () => {
    this.setState({
      addingDeviceDialog: true
    })
  }

  handleCloseAddDevice = () => {
    this.setState({
      addingDeviceDialog: false,
      newDevice: {
        id: "",
        name: "",
        type: ""
      },
    })
  }

  handleDeviceChange = name => event => {
    this.setState({
      newDevice: {
        ...this.state.newDevice,
      [name]: event.target.value
      }
    })
  }

  handleTextChange = name => event => {
    this.setState({
      [name]: event.target.value
    })
  }

  handleSelectDevice = device => _ => {
    this.setState({
      currentlySelectedDeviceId: device
    })
  }

  handleAddNewDevice = () => {
      axios.post('http://localhost:5000/add_device', this.state.newDevice).then(response => {
        console.log(response.data)
        this.setState({
          submitting: false
        })
      })
      .catch(err => {
        console.log(err)
        this.setState({
          submitting: false
      })
    })
    let deviceArray = this.state.devices
    deviceArray.push(this.state.newDevice)
    this.setState({
      devices: deviceArray, 
      newDevice: {
        id: "",
        name: "",
        type: ""
      },
      addingDeviceDialog: false,
    })
  }

  renderAddDeviceDialog = () => {
    return (
      <Dialog open={this.state.addingDeviceDialog}>
        <DialogContent>
          <Typography>Name</Typography> 
          <TextField
            variant="outlined"
            fullWidth
            value={this.state.newDevice.name}
            onChange={this.handleDeviceChange('name')}
          />
          <Typography>ID</Typography> 
          <TextField
            variant="outlined"
            fullWidth
            value={this.state.newDevice.id}
            onChange={this.handleDeviceChange('id')}
          />
        <Typography>Type</Typography> 
          <TextField
            variant="outlined"
            fullWidth
            value={this.state.newDevice.type}
            onChange={this.handleDeviceChange('type')}
          />
        </DialogContent>
        <DialogActions>
          <Button 
            variant="contained"
            onClick={this.handleCloseAddDevice} color="secondary">Close</Button>
          <Button 
            onClick={this.handleAddNewDevice}
            variant="contained"
            color="primary">Submit</Button>
        </DialogActions>
      </Dialog>
    )
  }

  renderConfig = () => {
    const { classes } = this.props
    return (
      <div>
        <Paper className={classes.configWrapper}>
            <Typography>Config</Typography>
            <Typography align="left" variant="caption">Output Path</Typography>
            <TextField
              variant="outlined"
              fullWidth
              value={this.state.outputPath}
              onChange={this.handleTextChange('outputPath')}
            />
            <Typography align="left" variant="caption">Interval Time in Seconds</Typography>
            <TextField
              variant="outlined"
              fullWidth
              type="number"
              value={this.state.intervalTime}
              onChange={this.handleTextChange('intervalTime')}
            />
            <Button 
              disabled={this.state.submitting}
              onClick={this.handleConfigSubmit}
              fullWidth 
              variant="contained" 
              color="primary">Save</Button>
        </Paper>      
      </div>
    )
  }

  renderDevice = device => {
    const { classes } = this.props
    return (
      <ListItem 
        onClick={this.handleSelectDevice(device.id)}
        className={classes.deviceItem}
        selected={this.state.currentlySelectedDeviceId === device.id}
        key={device.id}>
        <ListItemText primary={device.name} secondary={device.id} />
        <ListItemSecondaryAction>
          <IconButton onClick={this.handleRemoveDevice(device)} >
            <DeleteIcon />
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem>
    )
  }

  renderVideo = () => {
    const { classes } = this.props
    var currentDevice = this.state.devices.filter(item => {
      return item.id === this.state.currentlySelectedDeviceId
    })[0]
    return (
      <div className={classes.imageWrapper}>
          <img 
            className={classes.image}
            alt="cam2" src={`http://localhost:5000/${currentDevice.type}/${currentDevice.id}`} /> 
      </div>
    )
  }

  renderDeviceList = () => {
    const { classes } = this.props
    const { devices } = this.state
    return (
      <div className={classes.deviceListWrapper}>
        <Paper square>
          <List
            subheader={<ListSubheader>Device List</ListSubheader>} 
          >
            {devices.map(d => this.renderDevice(d))}
          </List>
          <div style={{padding: "0.5rem"}}>
            <Button 
              onClick={this.handleAddDevice}
              color="primary" variant="contained">Add</Button>
          </div>
        </Paper>
      </div>
    )
  }

  handleTabChange = (_, newValue) => {
    this.setState({
      tab: newValue
    })
  }

  renderMenu = () => {
    const { tab } = this.state
    return (
      <div>
        <Tabs
          variant="fullWidth"
          value={tab}
          onChange={this.handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Device List" />
          <Tab label="Config" />
        </Tabs>
        {
          tab === 0 && this.renderDeviceList()
        }
        {
          tab === 1 && this.renderConfig()
        }
      </div>
    )
  }

  render = () => {
    // const { classes } = this.props
    return (
      <div className="App">
        <header className="App-header">
          <Grid container>
            <Grid item xs={12} md={8}>
              {this.renderVideo()}
            </Grid>
            <Grid item xs={12} md={4}>
              {this.renderMenu()}
            </Grid>
          </Grid>
        </header>
        {this.renderAddDeviceDialog()}
      </div>
    );
  }
}

export default withStyles(styles)(App)