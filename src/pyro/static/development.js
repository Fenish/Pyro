let socket;

socket_events = {
  'hmr:update-document': updateDocument,
  'hmr:patch-document': patchDocument
};

function patchDocument(data) {
  for (const item of data) {
    const elementId = item.id;
    const changes = item.changes;
    const type = item.type;
    console.log(elementId, type, changes);

    switch (type) {
      case 'removed':
        const element = document.getElementById(elementId);
        if (element) {
          element.remove();
        }
        break;
      case 'added':
        const newElement = createElement(changes);
        const parentElementId = changes.parent.value;

        // If element has parent id
        // add the element to the parent
        // else add the element to the body
        if (parentElementId) {
          document.getElementById(parentElementId).appendChild(newElement);
        } else {
          document.body.appendChild(newElement);
        }
        break;
      case 'modified':
        updateElement(elementId, changes);
    }
  }
}

function updateElement(elementId, data) {
  const element = document.getElementById(elementId);

  if (data.class) {
    element.classList = data.class.value;
  }

  if (data.id) {
    element.id = data.id.value;
  }

  if (data.value) {
    if (data.value.value.type !== 'reactive') {
      element.innerHTML = data.value.value.value;
    }
  }

  if (data.location) {
    const parent = element.parentNode; // Get the parent of the current element
    const targetIndex = data.location.value; // The index where you want to move the element

    // Find all children of the parent
    const siblings = Array.from(parent.children);

    // Determine the reference sibling for insertion
    const referenceSibling = siblings[targetIndex]; // Get the target sibling based on the index

    // Move the current element after the reference sibling
    if (referenceSibling) {
      parent.insertBefore(element, referenceSibling.nextSibling);
    }
  }

  if (data.attributes) {
    // If the element has no attributes
    // remove all attributes except important ones
    if (data.attributes.value.length === 0) {
      const importantAttributes = [
        'id',
        'class',
        'style',
        'title',
        'href',
        'src',
        'alt',
        'value',
        'placeholder',
        'disabled',
        'checked',
        'selected',
        'role',
        'tabindex'
      ];
      const attributes = Array.from(element.attributes); // Get all attributes as an array
      attributes.forEach((attr) => {
        if (
          !importantAttributes.includes(attr.name) &&
          !attr.name.startsWith('on')
        ) {
          // Remove the attribute if it's not important and not an event attribute
          element.removeAttribute(attr.name); // Remove each attribute
        }
      });

      return;
    }

    // Add attributes
    for (const attribute of data.attributes.value) {
      element.setAttribute(attribute.name, attribute.value);
    }
  }
}

function createElement(data) {
  const element = document.createElement(data.tag.value);

  if (data.class.value) {
    element.classList.add(data.class.value);
  }

  if (data.id.value) {
    element.id = data.id.value;
  }

  if (data.value.value) {
    if (data.value.value.type !== 'reactive') {
      element.innerHTML = data.value.value.value;
    }
  }

  if (data.attributes.value) {
    for (const attribute of data.attributes.value) {
      element.setAttribute(attribute.name, attribute.value);
    }
  }

  return element;
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

  // Efficient way to listen to events in socket_events
  for (const [event, handler] of Object.entries(socket_events)) {
    socket.on(event, handler);
  }
}

// Set up the event listeners for connecting and disconnecting
window.addEventListener('load', connect, false);
window.addEventListener('beforeunload', disconnect, false);
