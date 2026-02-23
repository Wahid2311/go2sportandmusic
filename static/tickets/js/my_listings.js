function loadEvents() {
    const eventsContainer = document.getElementById('eventsContainer');
    
    eventsContainer.innerHTML = `
      <div class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading events...</span>
        </div>
        <p class="mt-3 text-muted">Loading events...</p>
      </div>
    `;

    fetch('/superadmin/events/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.text();
      })
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        const eventCards = doc.querySelectorAll('.user-card.event-card');
        
        if (eventCards.length === 0) {
          eventsContainer.innerHTML = `
            <div class="col-12 text-center py-5">
              <i class="bi bi-calendar-x" style="font-size: 3rem; color: #ccc;"></i>
              <p class="mt-3 text-muted">No events available for listing.</p>
            </div>
          `;
          return;
        }

        eventsContainer.innerHTML = '';
        
        eventCards.forEach(card => {
          const eventId = extractEventId(card);
          const eventName = extractEventName(card);
          const category = extractCategory(card);
          const stadium = extractStadium(card);
          const ticketsInfo = extractTicketsInfo(card);
          const timeLeft = extractTimeLeft(card);
          
          const eventCardHTML = createEventCardHTML({
            eventId,
            eventName,
            category,
            stadium,
            ticketsInfo,
            timeLeft
          });
          
          eventsContainer.innerHTML += eventCardHTML;
        });
      })
      .catch(error => {
        console.error('Error loading events:', error);
        eventsContainer.innerHTML = `
          <div class="col-12 text-center py-5">
            <i class="bi bi-exclamation-triangle" style="font-size: 3rem; color: #dc3545;"></i>
            <p class="mt-3 text-danger">Error loading events. Please try again.</p>
          </div>
        `;
      });
  }

  function extractEventId(card) {
  return card.dataset.eventId || null;
  }

  function extractEventName(card) {
    const nameElement = card.querySelector('.user-info-item span');
    return nameElement ? nameElement.textContent.trim() : 'Unknown Event';
  }

  function extractCategory(card) {
    const categoryBadge = card.querySelector('.user-type-badge');
    return categoryBadge ? categoryBadge.textContent.trim() : 'Other';
  }

  function extractStadium(card) {
    const stadiumElements = card.querySelectorAll('.user-info-item');
    for (let element of stadiumElements) {
      if (element.textContent.includes('bi-geo-alt') || element.innerHTML.includes('bi-geo-alt')) {
        return element.textContent.replace('bi-geo-alt', '').trim();
      }
    }
    return 'Unknown Venue';
  }

  function extractTicketsInfo(card) {
    const ticketsElement = card.querySelector('.user-info-item .bi-ticket-detailed')?.parentNode;
    if (ticketsElement) {
      const text = ticketsElement.textContent.trim();
      const match = text.match(/Tickets:\s*(\d+)\/(\d+)/);
      if (match) {
        return {
          sold: parseInt(match[1]),
          total: parseInt(match[2]),
          left: parseInt(match[2]) - parseInt(match[1])
        };
      }
    }
    return { sold: 0, total: 0, left: 0 };
  }

  function extractTimeLeft(card) {
    const timeElement = card.querySelector('.verification-badge');
    return timeElement ? timeElement.textContent.trim() : '';
  }

  // Function to create event card HTML
  function createEventCardHTML(eventData) {
    const categoryClass = getCategoryClass(eventData.category);
    
    return `
      <div class="col-xl-6 col-lg-12 mb-4 event-card-col" 
           data-event-name="${eventData.eventName.toLowerCase()}" 
           data-stadium="${eventData.stadium.toLowerCase()}" 
           data-category="${eventData.category.toLowerCase()}">
        <div class="card event-card h-100">

          <div class="card-body d-flex flex-column">
            <h5 class="event-name mb-1" style="min-height: auto; line-height: 1.3">
              ${eventData.eventName}
              <span class="event-category ${categoryClass}">${eventData.category}</span>
            </h5>

            <div class="event-info mb-2">
              <div class="event-date mb-1" style="margin-bottom: 0.3rem !important">
                <i class="bi bi-clock"></i>
                ${eventData.timeLeft || 'Time information not available'}
              </div>
              <div class="event-venue mb-1" style="margin-bottom: 0.3rem !important">
                <i class="bi bi-geo-alt"></i>
                <span class="text-truncate">${eventData.stadium}</span>
              </div>
            </div>

            <div class="event-tickets d-flex justify-content-between align-items-center mb-1">
              <span class="tickets-left">${eventData.ticketsInfo.left} left</span>
              <span class="tickets-sold">${eventData.ticketsInfo.sold} sold</span>
            </div>

            <div class="event-pricing mb-2">
              <div class="d-flex justify-content-between align-items-center">
                <small>Status:</small>
                <div>
                  <span class="price">${eventData.ticketsInfo.sold}/${eventData.ticketsInfo.total} Tickets</span>
                </div>
              </div>
            </div>

            <div class="event-actions mt-auto">
              <div class="d-grid gap-2">
                ${eventData.eventId ? 
                  `<a href="/events/${eventData.eventId}/create-listing/" class="btn btn-event-action">
                    Create Listing for This Event
                  </a>` :
                  `<button class="btn btn-event-action" disabled>
                    Create Listing (Event ID Missing)
                  </button>`
                }
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function getCategoryClass(category) {
    const categoryMap = {
      'sports': 'bg-primary',
      'festival': 'bg-success',
      'concert': 'bg-warning text-dark',
      'conference': 'bg-info',
      'theater': 'bg-purple'
    };
    return categoryMap[category.toLowerCase()] || 'bg-secondary';
  }

  document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('eventSearchInput');
    const eventsContainer = document.getElementById('eventsContainer');
    const searchResults = document.getElementById('eventSearchResults');
    
    searchResults.innerHTML = '';
    
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase().trim();
      
      searchResults.innerHTML = '';
      
      if (searchTerm.length === 0) {
        const eventCards = eventsContainer.querySelectorAll('.event-card-col');
        eventCards.forEach(card => {
          card.style.display = 'block';
        });
        return;
      }
      
      if (searchTerm.length < 2) {
        return; 
      }
      
      const eventCards = eventsContainer.querySelectorAll('.event-card-col');
      let hasResults = false;
      
      eventCards.forEach(card => {
        const eventName = card.getAttribute('data-event-name');
        const stadium = card.getAttribute('data-stadium');
        const category = card.getAttribute('data-category');
        
        if (eventName.includes(searchTerm) || stadium.includes(searchTerm) || category.includes(searchTerm)) {
          card.style.display = 'block';
          hasResults = true;
        } else {
          card.style.display = 'none';
        }
      });
      
      if (!hasResults) {
        searchResults.innerHTML = `
          <div class="alert alert-info">
            <i class="bi bi-info-circle"></i> No events found matching "${searchTerm}"
          </div>
        `;
      }
    });
    
    const modal = document.getElementById('addTicketModal');
    if (modal) {
      modal.addEventListener('shown.bs.modal', function() {
        searchInput.focus();
        
        loadEvents();
      });
      
      modal.addEventListener('hidden.bs.modal', function() {
        searchInput.value = '';
        searchResults.innerHTML = '';
      });
    }
  });
