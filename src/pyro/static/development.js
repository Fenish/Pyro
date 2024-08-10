let socket;
let pingInterval;

function connect() {
  if (socket && socket.connected) {
    return;
  }

  if (!socket) {
    socket = io.connect(window.location.origin, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: Infinity,
      transports: ['websocket']
    });
  }

  socketEvents();
}

function disconnect() {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}

function emit(event, data) {
  if (socket && socket.connected) {
    socket.emit(event, data);
  }
}

function ping() {
  emit('ping');
}

function socketEvents() {
  socket.on('connect', () => {
    console.log('Connected to server');
  });

  socket.on('disconnect', () => {
    console.log('Disconnected from server');
  });
}

// Set up the event listeners for connecting and disconnecting
window.addEventListener('load', connect, false);
window.addEventListener('beforeunload', disconnect, false);
