document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addRecordForm");
  const caseNumberInput = document.querySelector('input[name="case_number"]');
  const severitySelect = document.querySelector('select[name="severity"]');
  const titleInput = document.querySelector('input[name="title"]');
  const descriptionInput = document.querySelector(
    'textarea[name="description"]'
  );
  const suspectNameInput = document.querySelector('input[name="suspect_name"]');
  const suspectAgeInput = document.querySelector('input[name="suspect_age"]');
  const victimNameInput = document.querySelector('input[name="victim_name"]');
  const victimContactInput = document.querySelector(
    'input[name="victim_contact"]'
  );
  const locationInput = document.querySelector('input[name="location"]');
  const incidentDateInput = document.querySelector(
    'input[name="incident_date"]'
  );

  // Helper function to clear errors
  function clearError(element) {
    element.classList.remove("border-red-500");
    element.classList.add("border-slate-600");
    const errorDiv = element.parentElement.querySelector(".error-message");
    if (errorDiv) {
      errorDiv.remove();
    }
  }

  // Helper function to show errors
  function showError(element, message) {
    element.classList.remove("border-slate-600");
    element.classList.add("border-red-500");
    const errorDiv = document.createElement("div");
    errorDiv.className = "error-message text-red-400 text-sm mt-1";
    errorDiv.textContent = message;
    element.parentElement.appendChild(errorDiv);
  }

  // Real-time validation on blur
  caseNumberInput.addEventListener("blur", function () {
    clearError(this);
    if (!this.value.trim()) {
      showError(this, "Case number is required");
    } else if (!/^[A-Za-z0-9-]{5,}$/.test(this.value)) {
      showError(
        this,
        "Case number must be 5+ characters (letters, numbers, hyphens)"
      );
    }
  });

  severitySelect.addEventListener("change", function () {
    clearError(this);
    if (!this.value) {
      showError(this, "Please select a severity level");
    }
  });

  titleInput.addEventListener("blur", function () {
    clearError(this);
    if (!this.value.trim()) {
      showError(this, "Title is required");
    } else if (this.value.length < 5) {
      showError(this, "Title must be at least 5 characters");
    }
  });

  descriptionInput.addEventListener("blur", function () {
    clearError(this);
    if (!this.value.trim()) {
      showError(this, "Description is required");
    } else if (this.value.length < 10) {
      showError(this, "Description must be at least 10 characters");
    }
  });

  suspectNameInput.addEventListener("blur", function () {
    clearError(this);
    if (!this.value.trim()) {
      showError(this, "Suspect name is required");
    } else if (this.value.length < 2) {
      showError(this, "Suspect name must be at least 2 characters");
    }
  });

  suspectAgeInput.addEventListener("blur", function () {
    clearError(this);
    if (this.value === "") return; // Optional field
    const age = Number.parseInt(this.value);
    if (isNaN(age) || age < 0 || age > 120) {
      showError(this, "Age must be between 0 and 120");
    }
  });

  victimNameInput.addEventListener("blur", function () {
    clearError(this);
    if (this.value === "") return; // Optional field
    if (this.value.length < 2) {
      showError(this, "Victim name must be at least 2 characters");
    }
  });

  victimContactInput.addEventListener("blur", function () {
    clearError(this);
    if (this.value === "") return; // Optional field
    if (!/^[+]?[0-9\s\-()]{10,}$/.test(this.value)) {
      showError(this, "Please enter a valid phone number");
    }
  });

  locationInput.addEventListener("blur", function () {
    clearError(this);
    if (!this.value.trim()) {
      showError(this, "Location is required");
    } else if (this.value.length < 3) {
      showError(this, "Location must be at least 3 characters");
    }
  });

  incidentDateInput.addEventListener("blur", function () {
    clearError(this);
    if (!this.value) {
      showError(this, "Incident date is required");
    } else {
      const selectedDate = new Date(this.value);
      const now = new Date();
      if (selectedDate > now) {
        showError(this, "Incident date cannot be in the future");
      }
    }
  });

  // Form submission validation
  form.addEventListener("submit", (e) => {
    let isValid = true;

    // Clear all errors
    [
      caseNumberInput,
      severitySelect,
      titleInput,
      descriptionInput,
      suspectNameInput,
      suspectAgeInput,
      victimNameInput,
      victimContactInput,
      locationInput,
      incidentDateInput,
    ].forEach((field) => {
      clearError(field);
    });

    // Validate case number
    if (!caseNumberInput.value.trim()) {
      showError(caseNumberInput, "Case number is required");
      isValid = false;
    } else if (!/^[A-Za-z0-9-]{5,}$/.test(caseNumberInput.value)) {
      showError(caseNumberInput, "Case number must be 5+ characters");
      isValid = false;
    }

    // Validate severity
    if (!severitySelect.value) {
      showError(severitySelect, "Please select a severity level");
      isValid = false;
    }

    // Validate title
    if (!titleInput.value.trim() || titleInput.value.length < 5) {
      showError(titleInput, "Title must be at least 5 characters");
      isValid = false;
    }

    // Validate description
    if (!descriptionInput.value.trim() || descriptionInput.value.length < 10) {
      showError(descriptionInput, "Description must be at least 10 characters");
      isValid = false;
    }

    // Validate suspect name
    if (!suspectNameInput.value.trim()) {
      showError(suspectNameInput, "Suspect name is required");
      isValid = false;
    }

    // Validate incident date
    if (!incidentDateInput.value) {
      showError(incidentDateInput, "Incident date is required");
      isValid = false;
    } else {
      const selectedDate = new Date(incidentDateInput.value);
      const now = new Date();
      if (selectedDate > now) {
        showError(incidentDateInput, "Incident date cannot be in the future");
        isValid = false;
      }
    }

    // Validate location
    if (!locationInput.value.trim() || locationInput.value.length < 3) {
      showError(locationInput, "Location must be at least 3 characters");
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
    }
  });
});
