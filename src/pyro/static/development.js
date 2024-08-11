let socket;

socket_events = {
  'hmr:update-document': updateDocument,
  'hmr:patch-document': patchDocument
};

function createElement(data) {
  const element = document.createElement(data.tag);

  if (data.id) {
    element.id = data.id;
  }

  if (data.class) {
    element.className = data.class;
  }

  if (data.value && data.value.type === 'text') {
    element.textContent = data.value.value;
  }

  // Handle attributes and custom attributes if needed
  // data.attributes.forEach((attr) => {
  //   element.setAttribute(attr.name, attr.value);
  // });

  // data.custom_attributes.forEach((attr) => {
  //   element.setAttribute(attr.name, attr.value);
  // });

  return element;
}

function patchDocument(data) {
  for (const item of data) {
    const elementId = item.id;
    const changes = item.changes;

    const element = document.getElementById(elementId);
    for (const [key, value] of Object.entries(changes)) {
      switch (key) {
        case 'value':
          element.innerText = value.value;
          break;

        case 'children':
          const removedChildren = value.removed;
          if (removedChildren) {
            for (const child_id of removedChildren) {
              element.removeChild(document.getElementById(child_id));
            }
          }
          break;

        case 'elements':
          for (const child of value) {
            const new_element = createElement(child);
            element.appendChild(new_element);
          }
          break;
      }
    }
  }
}
function updateDocument(data) {
  document.documentElement.innerHTML = data;
}

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

function socketEvents() {
  socket.on('connect', () => {
    console.log('Connected to server');
    const currentPath = window.location.pathname;
    emit('hmr:path', currentPath);
  });

  socket.on('disconnect', () => {
    console.log('Disconnected from server');
  });

  for (const [event, handler] of Object.entries(socket_events)) {
    socket.on(event, handler);
  }
}

// Set up the event listeners for connecting and disconnecting
window.addEventListener('load', connect, false);
window.addEventListener('beforeunload', disconnect, false);
