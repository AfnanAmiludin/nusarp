/**
 * Global Tabulator utilities and helper functions
 * This file provides reusable components for Tabulator tables across the application
 */

// Namespace for our application
const AppUtils = window.AppUtils || {};

// Tabulator utilities namespace
AppUtils.TableUtils = {
  // Configuration objects
  config: {
    rowHeight: 32,
    defaultRowsPerPage: 10,
  },

  // DOM selectors
  selectors: {
    searchInput: '#global-search-input',
    clearSearchBtn: '#clear-search',
    activeFiltersContainer: '#active-filters',
    searchSuggestions: '#search-suggestions',
  },

  // Helper functions for escaping regex
  escapeRegExp: function(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  },

  // Debounce function to limit how often a function can be called
  debounce: function(func, wait) {
    let timeout;
    return function() {
      const context = this;
      const args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    };
  },

  // Add to the AppUtils.TableUtils object
  loadingOverlay: {
    /**
     * Show loading overlay on a table container
     * @param {string} tableSelector - CSS selector for the table container
     * @param {string} message - Optional loading message
     */
    show: function(tableSelector, message = 'Loading data...') {
      const container = document.querySelector(tableSelector);
      if (!container) return;
      
      // Create overlay if it doesn't exist
      let overlay = container.querySelector('.table-loading-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'table-loading-overlay';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        // Create dots for the pulse animation
        for (let i = 0; i < 3; i++) {
          const dot = document.createElement('div');
          dot.className = 'dot';
          spinner.appendChild(dot);
        }
        
        const messageElem = document.createElement('div');
        messageElem.className = 'loading-message';
        
        overlay.appendChild(spinner);
        overlay.appendChild(messageElem);
        container.appendChild(overlay);
      }
      
      // Update message
      overlay.querySelector('.loading-message').textContent = message;
      
      // Show overlay with fade-in
      overlay.style.display = 'flex';
      setTimeout(() => {
        overlay.style.opacity = '1';
      }, 10);
    },
    
    /**
     * Hide loading overlay
     * @param {string} tableSelector - CSS selector for the table container
     */
    hide: function(tableSelector) {
      const container = document.querySelector(tableSelector);
      if (!container) return;
      
      const overlay = container.querySelector('.table-loading-overlay');
      if (overlay) {
        // Fade out then hide
        overlay.style.opacity = '0';
        setTimeout(() => {
          overlay.style.display = 'none';
        }, 300);
      }
    }
  },

  // Formatters remain the same
  formatters: {
    highlightFormatter: function(cell, formatterParams, onRendered) {
      let value = cell.getValue();
      
      if (!value || typeof value !== 'string') {
        return value;
      }
      
      // Get search state from global object
      const searchState = AppUtils.TableUtils.searchState;
      let currentSearchTerm = searchState.currentSearchTerm;
      let hasActiveFilters = Object.keys(searchState.groupedFilters).length > 0;
      
      if (!hasActiveFilters && !currentSearchTerm) {
        return value; // Return original value without highlighting
      }

      if (hasActiveFilters) {
        Object.values(searchState.groupedFilters).forEach((filter) => {
          filter.values.forEach((term) => {
            if (term && term.length > 0) {
              let regex = new RegExp(`(${AppUtils.TableUtils.escapeRegExp(term)})`, 'gi');
              value = value.replace(
                regex,
                '<span class="search-highlight">$1</span>'
              );
            }
          });
        });
      }
      
      return value;
    },

    /**
     * Custom formatter for actions dropdown with vertical dots
     * @param {CellComponent} cell - The cell component
     * @param {Object} formatterParams - The formatter parameters
     * @param {Function} onRendered - Callback function when rendering is complete
     * @returns {string} - The formatted cell value
     */
    actionsFormatter: function(cell, formatterParams, onRendered) {
      return `
        <div class="dropdown-action">
          <button class="action-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
              <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
            </svg>
          </button>
          <div class="dropdown-content">
            <a href="#" class="edit-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="mr-2" viewBox="0 0 16 16">
                <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
              </svg>
              Editmm
            </a>
            <a href="#" class="delete-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="mr-2" viewBox="0 0 16 16">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
              </svg>
              Delete
            </a>
          </div>
        </div>
      `;
    }
  },

  // Search functionality
  searchState: {
    currentSearchTerm: '',
    groupedFilters: {},
  },

  // Search utilities
  search: {
    /**
     * Find matching values via AJAX
     * @param {string} searchValue - The search term
     * @param {Array} searchableColumns - The searchable column definitions
     * @param {Object} ajaxConfig - AJAX configuration for search suggestions
     * @returns {Promise} - Promise resolving to matching values
     */
    findMatchingValues: function(searchValue, searchableColumns, ajaxConfig) {
      return new Promise((resolve, reject) => {
        if (!searchValue) {
          resolve([]);
          return;
        }
        
        // Filter out columns with non-searchable types
        const textOnlyColumns = searchableColumns.filter(col => {
          // Define types that can be searched with text
          const searchableTypes = ['text', 'string', 'varchar', 'char'];
          // Check if column has a defined type and if it's searchable
          return !col.dataType || searchableTypes.includes(col.dataType.toLowerCase());
        });
        
        // Use AJAX to get suggestions
        $.ajax({
          url: ajaxConfig.suggestionUrl || ajaxConfig.ajaxURL,
          method: ajaxConfig.ajaxConfig || 'POST',
          data: {
            ...ajaxConfig.ajaxParams,
            search: searchValue,
            columns: textOnlyColumns.map(col => col.field)
          },
          success: function(response) {
            console.log(response.results);
    
            // Generate suggestions array based on response results
            const suggestions = response.results.map(item => {
              let itemSuggestions = [];
    
              // Iterate through each searchable column
              textOnlyColumns.forEach(column => {
                const field = column.field;
                const title = column.title;
                const value = item[field];
    
                // Only include if value exists, is a string, and contains searchValue (case-insensitive)
                if (value && typeof value === 'string' && value.toLowerCase().includes(searchValue.toLowerCase())) {
                  itemSuggestions.push({
                    field,
                    title,
                    value
                  });
                }
              });
    
              // Return item suggestions if any match
              return itemSuggestions;
            });
    
            // Flatten array of arrays into single array
            const results = suggestions.flat();
    
            // Send mapped results
            resolve(results);
          },
          error: function(xhr, status, error) {
            console.error('Search suggestions error:', error);
            resolve([]);  // Return empty array if error occurs
          }
        });
      });
    },  

    /**
     * Check if a row matches filter via server-side logic
     * @param {Object} rowData - The row data
     * @param {Object} filters - The grouped filter object
     * @returns {Promise} - Promise resolving to match result
     */
    rowMatchesFilter: function(rowData, filters) {
      return new Promise((resolve, reject) => {
        if (Object.keys(filters).length === 0) {
          resolve(true);
          return;
        }

        // Prepare filter parameters for server-side check
        const filterParams = Object.keys(filters).map(field => ({
          field,
          values: filters[field].values
        }));

        $.ajax({
          url: AppUtils.TableUtils.currentTableConfig?.ajaxURL,
          method: 'POST',
          data: {
            ...AppUtils.TableUtils.currentTableConfig?.ajaxParams,
            rowData: rowData,
            filters: filterParams
          },
          success: function(response) {
            resolve(response.results.match || false);
          },
          error: function(xhr, status, error) {
            console.error('Row match filter error:', error);
            resolve(false);
          }
        });
      });
    },

    /**
     * Add a filter value
     * @param {string} field - The field name
     * @param {string} value - The filter value
     * @param {string} title - The filter title/label
     */
    addFilterTag: function(field, value, title) {
      const searchState = AppUtils.TableUtils.searchState;
      
      // Initialize filter group if it doesn't exist
      if (!searchState.groupedFilters[field]) {
        searchState.groupedFilters[field] = {
          field: field,
          title: title,
          values: [],
        };
      }

      // Check if value already exists in this group
      if (searchState.groupedFilters[field].values.includes(value)) {
        return searchState.groupedFilters;
      }

      // Add value to group
      searchState.groupedFilters[field].values.push(value);

      return searchState.groupedFilters;
    },

    /**
     * Remove a value from a filter group
     * @param {string} field - The field name
     * @param {string} value - The filter value
     */
    removeFilterValue: function(field, value) {
      const searchState = AppUtils.TableUtils.searchState;
      
      // Check if filter group exists
      if (!searchState.groupedFilters[field]) {
        return searchState.groupedFilters;
      }
    
      // Remove value from group
      searchState.groupedFilters[field].values = searchState.groupedFilters[field].values.filter(
        (v) => v !== value
      );
    
      // Remove entire group if empty
      if (searchState.groupedFilters[field].values.length === 0) {
        delete searchState.groupedFilters[field];
      }
      
      return searchState.groupedFilters;
    },

    /**
     * Toggle column search visibility
     * @param {string} tableSelector - The CSS selector for the table container
     */
    toggleColumnSearch: function(tableSelector) {
      const table = Tabulator.findTable(tableSelector)[0];
      if (!table) return;

      const isFilterVisible = table.element.classList.contains('filters-visible');
      table.element.classList.toggle('filters-visible');

      const columns = table.getColumns();
      columns.forEach(column => {
        const headerElement = column.getElement();
        if (headerElement) {
          const filterElement = headerElement.querySelector('.tabulator-header-filter');
          if (filterElement) {
            filterElement.style.display = isFilterVisible ? 'none' : 'block';
          }
        }
      });
      table.redraw(true);
    },

    /**
     * Enhance filter inputs with search icon
     * @param {string} tableSelector - The CSS selector for the table container
     */
    enhanceFilterInputs: function(tableSelector) {
      const table = Tabulator.findTable(tableSelector)[0];
      if (!table) return;
      
      const filterInputs = table.element.querySelectorAll('.tabulator-header-filter input');
  
      filterInputs.forEach(input => {
        input.placeholder = "Search...";
        input.style.padding = '8px 10px 8px 36px';
        input.style.marginTop = '0.25rem';
  
        const wrapper = input.parentElement;
        wrapper.style.position = 'relative';
  
        const searchIcon = document.createElement('div');
        searchIcon.className = 'filter-search-icon';
        searchIcon.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>`;
        searchIcon.style.position = 'absolute';
        searchIcon.style.left = '12px';
        searchIcon.style.top = '50%';
        searchIcon.style.transform = 'translateY(-50%)';
        searchIcon.style.color = '#64748b';
        searchIcon.style.pointerEvents = 'none';
  
        wrapper.classList.add('custom-search');
        wrapper.appendChild(searchIcon);
      });
    },
  },

  /**
   * Initialize a table with searchable functionality using AJAX
   * @param {string} tableSelector - The CSS selector for the table container
   * @param {Array} columnDefs - The column definitions
   * @param {Object} options - Additional table options
   * @returns {Object} - The initialized table object and related methods
   */
  initializeSearchableTable: function(tableSelector, columnDefs, options = {}) {

    // Make sure the table container has position relative for proper overlay positioning
    const container = document.querySelector(tableSelector);
    if (container) {
      container.style.position = 'relative';
    }

    // Store DOM elements
    const elements = {
      tableContainer: document.querySelector(tableSelector),
      searchInput: document.querySelector(AppUtils.TableUtils.selectors.searchInput),
      clearSearchBtn: document.querySelector(AppUtils.TableUtils.selectors.clearSearchBtn),
      activeFiltersContainer: document.querySelector(AppUtils.TableUtils.selectors.activeFiltersContainer),
      searchSuggestions: document.querySelector(AppUtils.TableUtils.selectors.searchSuggestions)
    };

    const searchConfig = {
      minCharacters: 3,         // Minimum characters before auto-search
      autoSearchDelay: 2000,    // Auto-search delay in ms (2 seconds)
      typingIndicatorDelay: 500 // Show typing indicator after 500ms
    };
    
    // Default options with AJAX configuration
    const defaultOptions = {
      dataTree: true,
      dataTreeChildIndent: 20,
      dataTreeStartExpanded: false,
      layout: 'fitColumns',
      responsiveLayout: 'collapse',
      rowHeight: AppUtils.TableUtils.config.rowHeight,
      dataTreeExpandElement: "<span class='mr-2'><i class='ti ti-chevron-right'></i></span>",
      dataTreeCollapseElement: "<span class='mr-2'><i class='ti ti-chevron-down'></i></span>",
      dataTreeChildColumnCalcs: false,
      
      // AJAX Configuration
      ajaxURL: options.ajaxURL || '', // Required: URL to fetch data
      ajaxParams: options.ajaxParams || {}, // Optional: Additional parameters
      ajaxConfig: options.ajaxConfig || 'POST', // HTTP method
      
      // Pagination
      pagination: options.pagination !== undefined ? options.pagination : true,
      paginationSize: options.paginationSize || 10,
      paginationMode: options.paginationMode || 'remote', // Server-side pagination
    };
    
    // Store current table configuration globally for use in other methods
    AppUtils.TableUtils.currentTableConfig = {
      ...defaultOptions,
      ...options
    };
    
    // Merge default options with provided options
    const tableOptions = {
      ...defaultOptions,
      columns: columnDefs,
      dataLoader: false,         // Nonaktifkan loader data bawaan
      dataLoaderLoading: false,  // Nonaktifkan pesan loading data
      ...options
    };

    // Create the table
    const table = new Tabulator(tableSelector, {...tableOptions});

    // Tambahkan event listener untuk menggunakan custom overlay
    table.on("dataLoading", function() {
      AppUtils.TableUtils.loadingOverlay.show(tableSelector, 'Loading data...');
    });

    table.on("dataLoaded", function() {
      AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
    });

    // Juga tambahkan untuk ajax request jika menggunakan AJAX
    table.on("ajaxStarted", function() {
      AppUtils.TableUtils.loadingOverlay.show(tableSelector, 'Fetching data...');
    });

    table.on("ajaxComplete", function() {
      AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
    });

    table.on("tableBuilt", function() {
      markNonSearchableColumns();
    });
    
    // Define searchable columns - exclude actions and add dataType info
    const searchableColumns = columnDefs.filter(col => {
      // Exclude actions column
      if (col.field === 'actions') return false;
      
      // Exclude known non-text fields
      const nonTextTypes = ['date', 'datetime', 'time', 'integer', 'float', 'numeric', 'boolean'];
      if (col.dataType && nonTextTypes.includes(col.dataType.toLowerCase())) return false;
      
      return true;
    });

    // Add after the search input
    const searchHelpIcon = `
      <span class="search-help-icon ml-2 text-gray-400 cursor-help" title="Search applies to text columns only. Date, numeric, and action columns require filters.">
        <i class="ti ti-info-circle"></i>
      </span>
    `;
    $(elements.searchInput).after(searchHelpIcon);
    
    /**
     * Position the suggestions dropdown correctly
     */
    function positionSuggestions() {
      const inputRect = elements.searchInput.getBoundingClientRect();
      const suggestionsElem = $(elements.searchSuggestions);

      suggestionsElem.css({
        position: 'absolute',
        top: inputRect.bottom + window.scrollY + 'px',
        left: inputRect.left + window.scrollX + 'px',
        width: inputRect.width + 'px',
      });
    }
    
    /**
     * Show search suggestions with additional indicators
     * @param {string} searchValue - The current search value
     * @param {string} [indicatorType] - Type of indicator to show: 'typing', 'searching', 'error', or null
     * @param {string} [indicatorMessage] - Custom message for the indicator
     */
    function showSuggestions(searchValue, indicatorType = null, indicatorMessage = null) {
      // Clear previous suggestions
      $(elements.searchSuggestions).empty();
      
      // If there's an indicator to show, add it first
      if (indicatorType) {
        let indicatorHTML = '';
        
        switch (indicatorType) {
          case 'typing':
            indicatorHTML = `
              <div class="search-typing-indicator px-3 py-2 text-xs text-gray-500 flex items-center">
                <i class="ti ti-clock-hour-4 mr-1"></i>${indicatorMessage || `Pencarian otomatis dalam ${searchConfig.autoSearchDelay/1000} detik...`}
              </div>
            `;
            break;
          case 'searching':
            indicatorHTML = `
              <div class="search-loading-indicator px-3 py-2 text-xs text-blue-600 flex items-center">
                <i class="ti ti-loader mr-1 animate-spin"></i>${indicatorMessage || 'Mencari...'}
              </div>
            `;
            break;
          case 'error':
            indicatorHTML = `
              <div class="search-error-indicator px-3 py-2 text-xs text-red-500 flex items-center">
                <i class="ti ti-alert-circle mr-1"></i>${indicatorMessage || 'Terjadi kesalahan'}
              </div>
            `;
            break;
          case 'min-chars':
            indicatorHTML = `
              <div class="search-min-chars-indicator px-3 py-2 text-xs text-amber-500 flex items-center">
                <i class="ti ti-letter-case mr-1"></i>${indicatorMessage || `Minimal ${searchConfig.minCharacters} karakter untuk pencarian`}
              </div>
            `;
            break;
        }
        
        $(elements.searchSuggestions).append(indicatorHTML);
        $(elements.searchSuggestions).removeClass('hidden');
        positionSuggestions();
      }
    }
    
    /**
     * Update filter badges
     */
    function updateFilterBadges() {
      const searchState = AppUtils.TableUtils.searchState;
      
      // Clear existing badges
      $(elements.activeFiltersContainer).empty();
      
      // Only add content if there are filters
      if (Object.keys(searchState.groupedFilters).length > 0) {
        // Add the "Search:" label with a red Clear All badge
        const searchLabelHtml = `
          <div class="flex items-center">
            <span class="font-medium text-gray-600 mr-2">Search:</span>
            <button id="clear-all-filters" class="bg-red-500 text-white hover:bg-red-600 text-xs ml-1 flex items-center px-2 py-1 rounded">
              <i class="ti ti-trash mr-1"></i>Clear All
            </button>
          </div>
        `;
        $(elements.activeFiltersContainer).append(searchLabelHtml);
        
        // Create badge for each filter group
        Object.values(searchState.groupedFilters).forEach((filter) => {
          if (filter.values.length > 0) {
            // Create badge with all values
            const badgeHtml = `
              <div class="filter-tag inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs ml-2">
                <span class="font-medium mr-1">${filter.title}:</span>
                <div class="flex flex-wrap items-center">
                  ${filter.values
                    .map(
                      (value, index) => `
                    <div class="flex items-center mr-1 last:mr-0">
                      <span>${value}</span>
                      <button class="remove-filter ml-1 text-blue-800 hover:text-blue-600"
                             data-field="${filter.field}"
                             data-value="${value}">
                        <i class="ti ti-circle-x"></i>
                      </button>
                      ${index < filter.values.length - 1 ? '<span class="mx-1">|</span>' : ''}
                    </div>
                  `
                    )
                    .join('')}
                </div>
              </div>
            `;
    
            $(elements.activeFiltersContainer).append(badgeHtml);
          }
        });
      }
    }
    
    /**
     * Apply all active filters
     */
    function applyFilters() {
      const searchState = AppUtils.TableUtils.searchState;
      
      // If no filters, reset everything
      if (Object.keys(searchState.groupedFilters).length === 0) {
        AppUtils.TableUtils.resetTableCompletely();
        return;
      }
    
      console.log(searchState.groupedFilters);
      
      // Show loading overlay
      AppUtils.TableUtils.loadingOverlay.show(tableSelector, 'Filtering data...');
      
      // Prepare AJAX params for filtering
      const filterParams = Object.keys(searchState.groupedFilters).map(field => {
        const filterGroup = searchState.groupedFilters[field];
        return {
          field: filterGroup.field,
          values: filterGroup.values
        };
      });
    
      console.log(filterParams);
      
      // Send AJAX request with filter parameters
      $.ajax({
        url: tableOptions.ajaxURL,
        method: 'GET', // Use GET or POST depending on the API's requirements
        data: {
          ...tableOptions.ajaxParams,
          filters: JSON.stringify(filterParams) // Send filter parameters as a JSON string
        },
        success: function(response) {
          // Update table with new data from the server
          table.setData(response.results);
          // Hide loading overlay
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
        },
        error: function(xhr, status, error) {
          console.error('Error fetching filtered data:', error);
          // Hide loading overlay
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
        }
      });
    }        
    
    /**
     * Reset table completely
     */
    AppUtils.TableUtils.resetTableCompletely = function() {
      const searchState = AppUtils.TableUtils.searchState;
      
      // Clear the search input
      $(elements.searchInput).val('');
      
      // Hide the clear search button
      $(elements.clearSearchBtn).addClass('hidden');
      
      // Clear all filters
      searchState.groupedFilters = {};
      
      // Empty the active filters container
      $(elements.activeFiltersContainer).empty();
      
      // Reset any applied column search filters (if any)
      if (table) {
        table.clearFilter();
      }
    
      // Show loading overlay
      AppUtils.TableUtils.loadingOverlay.show(tableSelector, 'Resetting data...');
    
      // Reload original data without filters
      $.ajax({
        url: tableOptions.ajaxURL,
        method: 'GET',
        data: tableOptions.ajaxParams,
        success: function(response) {
          // Reset the table data to original (no filters)
          table.setData(response.results);
          // Hide loading overlay
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
        },
        error: function(xhr, status, error) {
          console.error('Error resetting the table:', error);
          // Hide loading overlay
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
        }
      });
    };
    
    /**
     * Expand nodes that match the current filters
     */
    AppUtils.TableUtils.expandMatchingNodes = function() {
      // For AJAX, this method might need server-side support
      // Typically, you'd send the current filters to the server
      // and get back information about which rows should be expanded
      table.setData({
        url: tableOptions.ajaxURL,
        params: {
          ...tableOptions.ajaxParams,
          expandMatching: true,
          filters: JSON.stringify(AppUtils.TableUtils.searchState.groupedFilters)
        }
      });
    };
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
      // Configuration for search behavior
      const searchConfig = {
        minCharacters: 3,         // Minimum characters before auto-search
        autoSearchDelay: 2000,    // Auto-search delay in ms (2 seconds)
        typingIndicatorDelay: 500 // Show typing indicator after 500ms
      };

      let searchTimeout;
      let typingIndicatorTimeout;

      // Handle input events - only for showing suggestions and typing indicator
      $(elements.searchInput).on('input', function() {
        const value = $(this).val();
        AppUtils.TableUtils.searchState.currentSearchTerm = value;
        
        // Clear previous timeouts
        clearTimeout(searchTimeout);
        clearTimeout(typingIndicatorTimeout);
        
        if (value) {
          $(elements.clearSearchBtn).removeClass('hidden');
          
          // Show suggestions based on input length
          if (value.length >= searchConfig.minCharacters) {
            // First show typing indicator in suggestions
            showSuggestions(value, 'typing');
            
            // Set auto-search after delay
            searchTimeout = setTimeout(() => {
              // Update to searching indicator
              showSuggestions(value, 'searching');
              
              // Perform actual search
              performSearch(value);
            }, searchConfig.autoSearchDelay);
          } else {
            // Show minimum character requirement
            showSuggestions(value, 'min-chars');
          }
        } else {
          // Hide suggestions and clear button if input is empty
          $(elements.searchSuggestions).addClass('hidden');
          $(elements.clearSearchBtn).addClass('hidden');
        }
      });

      // Handle Enter key for immediate search
      $(elements.searchInput).on('keydown', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          
          const value = $(this).val();
          
          // Clear any pending search
          clearTimeout(searchTimeout);
          
          // Perform search immediately if value exists and meets minimum length
          if (value && value.length >= searchConfig.minCharacters) {
            showSuggestions(value, 'searching');
            performSearch(value);
          } else if (value.length > 0 && value.length < searchConfig.minCharacters) {
            // Show minimum character warning
            showSuggestions(value, 'min-chars');
          } else {
            // Reset to original data if empty
            $(elements.searchSuggestions).addClass('hidden');
            table.setData({
              url: tableOptions.ajaxURL,
              params: tableOptions.ajaxParams
            });
          }
        } else if (e.key === 'Escape') {
          // Clear any pending search
          clearTimeout(searchTimeout);
          
          if ($(elements.searchSuggestions).is(':visible')) {
            $(elements.searchSuggestions).addClass('hidden');
          } else {
            // Clear input but keep filters
            $(this).val('');
            $(elements.clearSearchBtn).addClass('hidden');
          }
        }
      });

      // Helper function for performing the search
      function performSearch(value) {
        // Show searching indicator immediately
        showSuggestions(value, 'searching');
        
        // Show loading overlay
        AppUtils.TableUtils.loadingOverlay.show(tableSelector, 'Searching data...');
        
        // Only proceed if we have sufficient characters
        if (!value || value.length < searchConfig.minCharacters) {
          showSuggestions(value, 'min-chars');
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
          return;
        }
        
        // Create the Ajax configuration
        const searchParams = {
          ...tableOptions.ajaxParams,
          search: value
        };
      
        // Use AJAX to fetch search suggestions
        AppUtils.TableUtils.search.findMatchingValues(
          value, 
          searchableColumns, 
          tableOptions
        ).then(results => {
          // Store the search term
          AppUtils.TableUtils.searchState.currentSearchTerm = value;
          
          // Display results in the suggestion dropdown
          displaySearchResults(value, results);
          
          // Hide loading overlay
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
        }).catch(error => {
          console.error('Error performing search:', error);
          showSuggestions(value, 'error', 'Gagal memuat data');
          
          // Hide loading overlay
          AppUtils.TableUtils.loadingOverlay.hide(tableSelector);
        });
      }

      // New function to display search results without making another AJAX call
      function displaySearchResults(searchValue, results) {
        // Clear previous suggestions
        $(elements.searchSuggestions).empty();
        
        if (results.length > 0) {
          // Group results by column
          const groupedResults = {};
          
          // Track unique values for each field
          const uniqueValues = {};
          
          // Process results to extract unique values
          results.forEach((result) => {
            // Initialize field in tracking objects if not exist
            if (!groupedResults[result.field]) {
              groupedResults[result.field] = [];
              uniqueValues[result.field] = new Set();
            }
            
            // Only add the result if this value hasn't been seen before for this field
            if (!uniqueValues[result.field].has(result.value)) {
              uniqueValues[result.field].add(result.value);
              groupedResults[result.field].push(result);
            }
          });

          // Add column headers and unique values
          Object.keys(groupedResults).forEach((field) => {
            const fieldResults = groupedResults[field];
            if (fieldResults.length > 0) {
              const columnTitle = fieldResults[0].title;

              // Add column header
              $(elements.searchSuggestions).append(`
                <div class="px-3 py-1 text-xs text-gray-500 bg-gray-100">${columnTitle}</div>
              `);

              // Add unique values
              fieldResults.forEach((result) => {
                $(elements.searchSuggestions).append(`
                  <div class="suggestion-item px-3 py-2 hover:bg-gray-100 cursor-pointer"
                      data-field="${result.field}"
                      data-value="${result.value}"
                      data-title="${result.title}">
                    <span class="search-highlight">${result.value}</span>
                  </div>
                `);
              });
            }
          });

          // Show suggestions
          $(elements.searchSuggestions).removeClass('hidden');
          positionSuggestions();
        } else {
          // No results found
          $(elements.searchSuggestions).append(`
            <div class="px-3 py-2 text-sm text-gray-500">
              <p>Tidak ada hasil yang ditemukan untuk "${searchValue}"</p>
              <hr class="my-2 border-t border-gray-200">
              <p class="text-xs text-gray-400 mt-1">
                <i class="ti ti-info-circle mr-1"></i>
                Pencarian hanya berlaku untuk kolom teks. Kolom tanggal, numerik, dan aksi memerlukan filter.
              </p>
            </div>
          `);
          $(elements.searchSuggestions).removeClass('hidden');
          positionSuggestions();
        }
      }
  
      // Handle search suggestion clicks
      $(document).on('click', '.suggestion-item', function () {
        const field = $(this).data('field');
        const value = $(this).data('value');
        const title = $(this).data('title');
  
        AppUtils.TableUtils.search.addFilterTag(field, value, title);
        updateFilterBadges();
        applyFilters();
        
        $(elements.searchInput).val('').focus();
        $(elements.searchSuggestions).addClass('hidden');
      });
  
      // Handle filter tag remove button clicks
      $(document).on('click', '.remove-filter', function () {
        const field = $(this).data('field');
        const value = $(this).data('value');
  
        AppUtils.TableUtils.search.removeFilterValue(field, value);
        updateFilterBadges();
        applyFilters();
        
        // Check if no filters remain - if so, do a complete reset
        const searchState = AppUtils.TableUtils.searchState;
        if (Object.keys(searchState.groupedFilters).length === 0) {
          AppUtils.TableUtils.resetTableCompletely();
        }
      });
  
      // Add handler for the Clear All button
      $(document).on('click', '#clear-all-filters', function() {
        AppUtils.TableUtils.resetTableCompletely();
      });
  
      // Hide suggestions when clicking outside
      $(document).on('click', function (e) {
        if (!$(e.target).closest('#search-suggestions, #global-search-input').length) {
          $(elements.searchSuggestions).addClass('hidden');
        }
      });
  
      // Clear all filters
      $(elements.clearSearchBtn).on('click', function () {
        AppUtils.TableUtils.resetTableCompletely();
      });
  
      // Add window resize listener to reposition suggestions
      $(window).on('resize', function () {
        if ($(elements.searchSuggestions).is(':visible')) {
          positionSuggestions();
        }
      });
  
      // Handle Escape key
      $(elements.searchInput).on('keydown', function (e) {
        if (e.key === 'Escape') {
          // Clear any pending search
          clearTimeout(searchTimeout);
          $('.search-typing-indicator').remove();
          
          if ($(elements.searchSuggestions).is(':visible')) {
            $(elements.searchSuggestions).addClass('hidden');
          } else {
            // Clear input but keep filters
            $(this).val('');
            $(elements.clearSearchBtn).addClass('hidden');
          }
        }
      });
  
      // Focus search input with / key
      $(document).on('keydown', function (e) {
        if (e.key === '/' && document.activeElement !== elements.searchInput) {
          e.preventDefault();
          elements.searchInput.focus();
        }
      });
  
      // Add placeholder animation effect on focus
      $(elements.searchInput).on('focus', function () {
        this.placeholder = `Tekan Enter atau ketik min. ${searchConfig.minCharacters} karakter`;
        $(this).addClass('ring-2 ring-blue-400 border-blue-400');
      });

      $(elements.searchInput).on('blur', function () {
        this.placeholder = 'Cari di semua kolom...';
        $(this).removeClass('ring-2 ring-blue-400 border-blue-400');
      });
    }
    
    /**
     * Initialize dropdown handling
     */
    function initializeDropdowns() {
      function closeAllDropdowns() {
        $('.dropdown-content').removeClass('show');
      }

      $(document).on('click', '.action-btn', function (e) {
        e.stopPropagation();
        closeAllDropdowns();

        var dropdown = $(this).next('.dropdown-content');
        dropdown.addClass('show');

        // Set fixed positions for the dropdown
        var dropdownClone = dropdown.clone(true);
        var btnPos = $(this).offset();

        $('body > .dropdown-content').remove();

        dropdown.removeClass('show');

        dropdownClone
          .css({
            position: 'fixed',
            top: btnPos.top + $(this).outerHeight(),
            left: btnPos.left - $(this).outerWidth() * 7,
            zIndex: 9999,
          })
          .appendTo('body')
          .addClass('show');

        dropdownClone.find('a').on('click', function (e) {
          e.stopPropagation();
          closeAllDropdowns();
        });
      });

      $(document).on('click', function () {
        closeAllDropdowns();
      });
    }

    // Instead of adding after the input, let's place it inside with proper positioning
    function enhanceGlobalSearch() {
      const searchInput = $(elements.searchInput);
      
      // Add positioning to the search input container
      searchInput.parent().css('position', 'relative');
      
      // Remove any existing help icons to prevent duplication
      searchInput.parent().find('.search-help-icon').remove();
      
      // Create the search icon for the LEFT side
      const searchIcon = $(`
        <span class="search-icon text-gray-400" 
              style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); z-index: 10; pointer-events: none;">
          <i class="ti ti-search"></i>
        </span>
      `);
      
      // Create the help icon for the RIGHT side
      const helpIcon = $(`
        <span class="search-help-icon text-gray-400 cursor-help" 
              title="Pencarian hanya berlaku untuk kolom teks. Kolom tanggal, numerik, dan aksi memerlukan filter."
              style="position: absolute;right: 240px;top: 50%;transform: translateY(-50%);z-index: 10;">
          <i class="ti ti-info-circle"></i>
        </span>
      `);
      
      // Insert both icons into the parent container
      searchInput.parent().append(searchIcon);
      searchInput.parent().append(helpIcon);
      
      // Adjust padding on both sides of the input to prevent text overlap with icons
      searchInput.css({
        'padding-left': '30px',  // Padding untuk ikon pencarian di kiri
        'padding-right': '30px'  // Padding untuk ikon bantuan di kanan
      });
    }

    function markNonSearchableColumns() {
      // Define the non-searchable column types
      const nonTextTypes = ['date', 'datetime', 'time', 'integer', 'float', 'numeric', 'boolean'];
      
      // Get all column definitions
      const columns = table.getColumns();
      
      // Iterate through each column
      columns.forEach(column => {
        const columnDef = column.getDefinition();
        const field = columnDef.field;
        const dataType = columnDef.dataType;
        
        // Check if this is a non-searchable column
        const isNonSearchable = field === 'actions' || 
          (dataType && nonTextTypes.includes(dataType.toLowerCase()));
        
        if (isNonSearchable) {
          // Get the header element for this column
          const headerElement = column.getElement();
          
          if (headerElement) {
            // Create a filter icon element
            const filterIcon = document.createElement('span');
            filterIcon.className = 'ml-1 text-xs text-gray-400';
            filterIcon.innerHTML = '<i class="ti ti-filter"></i>';
            filterIcon.title = 'Gunakan filter kolom (bukan pencarian global) untuk kolom ini';
            
            // Find the title element within the header
            const titleElement = headerElement.querySelector('.tabulator-col-title');
            if (titleElement) {
              titleElement.appendChild(filterIcon);
            }
          }
        }
      });
    }
    
    /**
     * Set up CSS styles for the table
     */
    function setupTableStyles() {
      $('<style>')
        .prop('type', 'text/css')
        .html(
          `
          .dropdown-action { position: relative; display: inline-block; }
            .action-btn { background: none; border: none; cursor: pointer; color: #6b7280; padding: 3px; }
            .action-btn:hover { color: #374151; }
            .dropdown-content { display: none; position: absolute; left: 0; background-color: #fff; min-width: 160px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); z-index: 9999; border-radius: 4px; overflow: hidden; font-size: 13px; }
            .dropdown-content.show { display: block; }
            .dropdown-content a { color: #374151; padding: 8px 12px; text-decoration: none; display: flex; align-items: center; }
            .dropdown-content a:hover { background-color: #f3f4f6; }
            .edit-btn { color: #2563eb; }
            .delete-btn { color: #dc2626; }
            .action-cell { padding: 0 !important; }
            .dropdown-content svg { margin-right: 8px; }
            .filter-tag { transition: all 0.2s; }
            .filter-tag:hover { background-color: #dbeafe; }
            .search-highlight { background-color: #FFEB3B; color: #000; font-weight: 500; padding: 0 2px; border-radius: 2px; }:
            #search-suggestions { max-height: 300px; overflow-y: auto; z-index: 1000; }
            .suggestion-item { transition: background-color 0.2s; }
            .suggestion-item:hover { background-color: #f3f4f6; }
            .search-highlight {background-color: #FFEB3B; color: #000; font-weight: 500; padding: 0 2px; border-radius: 2px;}
            .current-search-highlight {background-color: #FF9800; color: #000; font-weight: 500; padding: 0 2px; border-radius: 2px;}
            @keyframes search-pulse {0% {background-color: rgba(255, 235, 59, 0.3);} 50% {background-color: rgba(255, 235, 59, 0.6);} 100% {background-color: rgba(255, 235, 59, 0.3);}}
            .search-row-highlight {animation: search-pulse 1.5s ease-in-out 1;}
            .tabulator-row.tabulator-row-even.search-row-highlight:hover {background-color: rgba(255, 235, 59, 0.1);}
            .tabulator-row.tabulator-row-odd.search-row-highlight:hover {background-color: rgba(255, 235, 59, 0.15);}
            .tabulator-header-filter input {
              border-radius: 6px;
              border: 1px solid #e2e8f0;
              padding: 8px 10px 8px 36px;
              font-size: 0.875rem;
              width: 100%;
              background-color: #f8fafc;
              transition: all 0.2s ease;
              box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
              height: 38px;
            }

            .tabulator-header-filter input:focus {
              outline: none;
              border-color: #3b82f6;
              box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
              background-color: #fff;
            }

            .tabulator-header-filter.custom-search::before {
              display: none !important;
            }
            
            .tabulator-header-filter {
              display: none;
            }

            .search-typing-indicator, 
            .search-loading-indicator, 
            .search-error-indicator,
            .search-min-chars-indicator {
              border-bottom: 1px solid rgba(229, 231, 235, 0.5);
              font-weight: 500;
            }

            #search-suggestions {
              max-height: 300px;
              overflow-y: auto;
              z-index: 1000;
              box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
              border-radius: 0.375rem;
              border: 1px solid rgba(229, 231, 235, 1);
              background-color: white;
            }
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
            .animate-spin {
              animation: spin 1s linear infinite;
            }
            /* Modern loading animation styles */
            .table-loading-overlay {
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background-color: rgba(255, 255, 255, 0.85);
              display: none;
              opacity: 0;
              transition: opacity 0.3s ease;
              z-index: 100;
              justify-content: center;
              align-items: center;
              flex-direction: column;
              backdrop-filter: blur(2px);
            }

            /* Pulse loading animation */
            .loading-spinner {
              display: flex;
              align-items: center;
              justify-content: center;
              margin-bottom: 16px;
            }

            .loading-spinner .dot {
              width: 12px;
              height: 12px;
              border-radius: 50%;
              background-color: #3b82f6;
              margin: 0 4px;
              animation: pulse 1.5s infinite ease-in-out;
            }

            .loading-spinner .dot:nth-child(1) {
              animation-delay: 0s;
            }

            .loading-spinner .dot:nth-child(2) {
              animation-delay: 0.3s;
            }

            .loading-spinner .dot:nth-child(3) {
              animation-delay: 0.6s;
            }

            .loading-message {
              color: #334155;
              font-size: 16px;
              font-weight: 500;
              letter-spacing: 0.025em;
              text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8);
            }

            @keyframes pulse {
              0%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
              }
              50% {
                transform: scale(1.2);
                opacity: 1;
              }
            }

            /* For table container */
            .tabulator {
              position: relative;
            }
        `
        )
        .appendTo('head');
    }
    
    // Initialize everything
    setupTableStyles();
    setupEventListeners();
    initializeDropdowns();
    enhanceGlobalSearch();
    AppUtils.TableUtils.search.enhanceFilterInputs(tableSelector);
    
    // Return the initialized table object and related methods
    return {
      table,
      resetTable: AppUtils.TableUtils.resetTableCompletely,
      applyFilters: applyFilters,
      updateFilterBadges: updateFilterBadges
    };
  }
};

// Make sure the namespace is globally available
window.AppUtils = AppUtils;