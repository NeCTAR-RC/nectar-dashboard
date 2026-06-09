/*
 * DNS service name auto-population.
 *
 * Derives a suggested DNS zone (<sanitised-project-name>.cloud.edu.au) from the
 * project name as the user types it, mirroring the sanitisation logic in
 * nectar-tools/expiry/archiver.py, and writes it into the #id_dns_domain field.
 */

function get_dns_service_name(project_name) {
  var domain_name = 'cloud.edu.au';
  var zone;

  // Setting an arbitrary length for new project names to >=5
  if (project_name.length < 5) {
    zone = '';
  } else {
    // Copied from nectar-tools/expiry/archiver.py
    var name = project_name.toLowerCase()
                           .replace(/_/g, '-')
                           .replace(/[^a-z0-9-]+/g, '')
                           .replace(/(-)\1+/g, '$1')
                           .replace(/^[^a-z0-9]/g, '')
                           .substring(0, 62)
                           .replace(/[^a-z0-9]$/g, '');
    zone = name + '.' + domain_name;
  }
  return zone;
}

function populate_dns_service_name() {
  if ($('#id_project_name').length) {
    var project_name = $('#id_project_name').val();
    var zone = get_dns_service_name(project_name);
    $('#id_dns_domain').val(zone);
  }
}

$('#id_project_name').on('input', function(e) {
  populate_dns_service_name();
});
