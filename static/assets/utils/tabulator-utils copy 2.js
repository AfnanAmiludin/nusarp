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

  // Formatters for cells
  formatters: {
    /**
     * Custom formatter that highlights search matches
     * @param {CellComponent} cell - The cell component
     * @param {Object} formatterParams - The formatter parameters
     * @param {Function} onRendered - Callback function when rendering is complete
     * @returns {string} - The formatted cell value
     */
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
      
      // Apply highlighting for active filters
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
              Edit
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
     * Find all matching column values for the current search term
     * @param {Array} tableData - The table data array
     * @param {string} searchValue - The search term
     * @param {Array} searchableColumns - The searchable column definitions
     * @returns {Array} - The matched values for each column
     */
    findMatchingValues: function(tableData, searchValue, searchableColumns) {
      if (!searchValue) return [];

      const results = [];
      searchValue = searchValue.toLowerCase();

      // Check each searchable column
      searchableColumns.forEach((column) => {
        const field = column.field;
        const title = column.title;

        // Collect all unique values that match the search
        const matchingValues = new Set();

        // Function to check values recursively
        function checkData(data) {
          if (
            data[field] &&
            typeof data[field] === 'string' &&
            data[field].toLowerCase().includes(searchValue)
          ) {
            matchingValues.add(data[field]);
          }

          // Check children if any
          if (data.children && data.children.length) {
            data.children.forEach((child) => checkData(child));
          }
        }

        // Process all rows
        tableData.forEach((row) => checkData(row));

        // Add all matches to results
        matchingValues.forEach((value) => {
          results.push({
            field,
            title,
            value,
          });
        });
      });

      return results;
    },

    /**
     * Check if a row or any of its children match the filter
     * @param {RowComponent} row - The table row component 
     * @param {Object} filters - The grouped filter object
     * @returns {boolean} - Whether the row matches the filters
     */
    rowMatchesFilter: function(row, filters) {
      // Get the full row data, including nested data
      let rowData = row.getData();

      // Check if current row matches filters
      let directMatch = Object.keys(filters).every((field) => {
        const values = filters[field].values;
        return values.some(
          (value) =>
            rowData[field] &&
            typeof rowData[field] === 'string' &&
            rowData[field].toLowerCase().includes(value.toLowerCase())
        );
      });

      if (directMatch) return true;

      // If not a direct match, check children recursively
      function checkChildren(data) {
        // Check if current data matches filters
        let childMatch = Object.keys(filters).every((field) => {
          const values = filters[field].values;
          return values.some(
            (value) =>
              data[field] &&
              typeof data[field] === 'string' &&
              data[field].toLowerCase().includes(value.toLowerCase())
          );
        });

        if (childMatch) return true;

        // Recursively check nested children
        if (data.children && data.children.length) {
          return data.children.some((child) => checkChildren(child));
        }

        return false;
      }

      // Check children of the current row
      if (rowData.children && rowData.children.length) {
        return rowData.children.some((child) => checkChildren(child));
      }

      return false;
    },

    /**
     * Add a filter value to a grouped filter
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
        return; // Skip if already exists
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
        return;
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
     * Show or hide column filters
     * @param {string} tableSelector - The CSS selector for the table container
     * @returns {void}
     * @example AppUtils.TableUtils.toggleColumnSearch('#my-table');
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
     * @returns {void}
     * @example AppUtils.TableUtils.enhanceFilterInputs('#my-table');
     * @description Enhances the filter inputs with a search icon and custom styles
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
   * Initialize a table with searchable functionality
   * @param {string} tableSelector - The CSS selector for the table container
   * @param {Array} tableData - The table data array 
   * @param {Array} columnDefs - The column definitions
   * @param {Object} options - Additional table options
   * @returns {Object} - The initialized table object and related methods
   */
  initializeSearchableTable: function(tableSelector, tableData, columnDefs, options) {
    // Store DOM elements
    const elements = {
      tableContainer: document.querySelector(tableSelector),
      searchInput: document.querySelector(AppUtils.TableUtils.selectors.searchInput),
      clearSearchBtn: document.querySelector(AppUtils.TableUtils.selectors.clearSearchBtn),
      activeFiltersContainer: document.querySelector(AppUtils.TableUtils.selectors.activeFiltersContainer),
      searchSuggestions: document.querySelector(AppUtils.TableUtils.selectors.searchSuggestions)
    };
    
    // Default options
    const defaultOptions = {
      dataTree: true,
      dataTreeChildIndent: 20,
      dataTreeStartExpanded: false,
      layout: 'fitColumns',
      responsiveLayout: 'collapse',
      rowHeight: AppUtils.TableUtils.config.rowHeight,
      dataTreeExpandElement: "<span class='mr-2'><i class='ti ti-chevron-right'></i></span>",
      dataTreeCollapseElement: "<span class='mr-2'><i class='ti ti-chevron-down'></i></span>",
      dataTreeChildColumnCalcs: false
    };
    
    // Merge default options with provided options
    const tableOptions = {...defaultOptions, ...options, data: tableData, columns: columnDefs};
    
    // Create the table
    const table = new Tabulator(tableSelector, tableOptions);
    
    // Define searchable columns - exclude actions
    const searchableColumns = columnDefs.filter(col => col.field !== 'actions');
    
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
     * Show search suggestions
     * @param {string} searchValue - The current search value
     */
    function showSuggestions(searchValue) {
      const results = AppUtils.TableUtils.search.findMatchingValues(tableData, searchValue, searchableColumns);

      // Clear previous suggestions
      $(elements.searchSuggestions).empty();

      if (results.length > 0) {
        // Group results by column
        const groupedResults = {};
        results.forEach((result) => {
          if (!groupedResults[result.field]) {
            groupedResults[result.field] = [];
          }
          groupedResults[result.field].push(result);
        });

        // Add column headers and values
        Object.keys(groupedResults).forEach((field) => {
            const fieldResults = groupedResults[field];
            const columnTitle = fieldResults[0].title;
  
            // Add column header
            $(elements.searchSuggestions).append(`
              <div class="px-3 py-1 text-xs text-gray-500 bg-gray-100">${columnTitle}</div>
            `);
  
            // Add values
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
          });
  
          // Show suggestions
          $(elements.searchSuggestions).removeClass('hidden');
          positionSuggestions();
        } else {
          $(elements.searchSuggestions).addClass('hidden');
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
        
        // Reset table to show all rows first
        table.clearFilter();
      
        // If no filters, reset everything
        if (Object.keys(searchState.groupedFilters).length === 0) {
          AppUtils.TableUtils.resetTableCompletely();
          return;
        }
      
        // Custom filter function
        function customFilter(data) {
          // Check if current row or any of its children match the filters
          function checkRowAndChildren(rowData) {
            // Check if current row matches all filter conditions
            const directMatch = Object.keys(searchState.groupedFilters).every((field) => {
              const values = searchState.groupedFilters[field].values;
              return values.some(
                (value) =>
                  rowData[field] &&
                  typeof rowData[field] === 'string' &&
                  rowData[field].toLowerCase().includes(value.toLowerCase())
              );
            });
      
            if (directMatch) return true;
      
            // Check nested children
            if (rowData.children && rowData.children.length) {
              return rowData.children.some((child) => {
                // Recursively check each child
                return checkRowAndChildren(child);
              });
            }
      
            return false;
          }
      
          return checkRowAndChildren(data);
        }
      
        // Apply the custom filter
        table.setFilter(customFilter);
      
        // Force a refresh to ensure highlighting updates on all visible cells
        table.redraw(true);
      
        // Expand matching rows
        AppUtils.TableUtils.expandMatchingNodes();
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
        
        // Clear table filter
        table.clearFilter();
        
        // Force a complete redraw to remove all highlighting
        table.redraw(true);
        
        // Collapse all tree nodes
        table.getRows().forEach((row) => {
          if (row.getTreeChildren().length) {
            row.treeCollapse();
          }
        });
      };
      
      /**
       * Expand nodes that match the current filters
       */
      AppUtils.TableUtils.expandMatchingNodes = function() {
        const searchState = AppUtils.TableUtils.searchState;
        
        // First collapse all
        table.getRows().forEach((row) => {
          if (row.getTreeChildren().length) {
            row.treeCollapse();
          }
        });
  
        // Then expand ones with matching children
        if (Object.keys(searchState.groupedFilters).length > 0) {
          table.getRows().forEach((row) => {
            const hasMatchingChild = row
              .getTreeChildren()
              .some((child) => AppUtils.TableUtils.search.rowMatchesFilter(child, searchState.groupedFilters));
  
            if (hasMatchingChild) {
              row.treeExpand();
              AppUtils.TableUtils.expandChildrenWithMatches(row);
            }
          });
        }
      };
      
      /**
       * Recursively expand children that have matches
       * @param {RowComponent} parentRow - The parent table row
       */
      AppUtils.TableUtils.expandChildrenWithMatches = function(parentRow) {
        const searchState = AppUtils.TableUtils.searchState;
        
        parentRow.getTreeChildren().forEach((childRow) => {
          const hasMatchingChild = childRow
            .getTreeChildren()
            .some((child) => AppUtils.TableUtils.search.rowMatchesFilter(child, searchState.groupedFilters));
  
          if (hasMatchingChild) {
            childRow.treeExpand();
            AppUtils.TableUtils.expandChildrenWithMatches(childRow);
          }
        });
      };
      
      /**
       * Set up event listeners
       */
      function setupEventListeners() {
        // Handle input events
        $(elements.searchInput).on(
          'input',
          AppUtils.TableUtils.debounce(function () {
            const value = $(this).val();
            AppUtils.TableUtils.searchState.currentSearchTerm = value;
  
            if (value) {
              showSuggestions(value);
              $(elements.clearSearchBtn).removeClass('hidden');
  
              // Force refresh of table cells to update highlighting for the current search term
              table.redraw(true);
            } else {
              $(elements.searchSuggestions).addClass('hidden');
              $(elements.clearSearchBtn).addClass('hidden');
              table.redraw(true); // Refresh when cleared too
            }
          }, 300)
        );
  
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
          
          // Force a complete redraw to refresh all highlighting
          table.redraw(true);
          
          // Check if no filters remain - if so, do a complete reset like clear search button
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
            if ($(elements.searchSuggestions).is(':visible')) {
              $(elements.searchSuggestions).addClass('hidden');
            } else {
              // Clear input but keep filters
              $(this).val('');
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
          this.placeholder = 'Ketik untuk mencari...';
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
          `
        )
        .appendTo('head');
    }
    
    // Initialize everything
    setupTableStyles();
    setupEventListeners();
    initializeDropdowns();
    AppUtils.TableUtils.search.enhanceFilterInputs(tableSelector);
    // always hide header filter on init tabulator-header-filter display: none;
    
    
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