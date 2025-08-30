(function(global) {
  // Minimal deterministic UMD-like bundle that exposes a .default component
  // which simply delegates to the existing SimpleFormComponent defined
  // in the generated HTML. This gives us a stable, small embedded bundle
  // for offline/deterministic tests.
  const RJSF = {
    default: function(props) {
      if (global && global.SimpleFormComponent) {
        return global.SimpleFormComponent(props);
      }
      // Fallback simple element using plain DOM if React not available
      return null;
    }
  };

  // Provide a minimal validator shape expected by our generator/tests
  RJSF.validator = { ajv8: {} };

  // Expose as JSONSchemaForm global used earlier
  global.JSONSchemaForm = RJSF;
})(typeof window !== 'undefined' ? window : this);
