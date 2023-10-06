function redirectToProteinEndpoint() {
  const proteinId = document.getElementById("protein-input").value;
  const endpoint = `/api/protein/${proteinId}`;
  window.location.href = endpoint;
}

function redirectToPfamEndpoint() {
  const pfamId = document.getElementById("pfam-input").value;
  const endpoint = `/api/pfam/${pfamId}`;
  window.location.href = endpoint;
}
function redirectToProteinsByTaxaEndpoint() {
  const taxaId = document.getElementById("taxa-proteins-input").value;
  const endpoint = `/api/proteins/${taxaId}`;
  window.location.href = endpoint;
}

function redirectToPfamsByTaxaEndpoint() {
  const taxaId = document.getElementById("taxa-pfams-input").value;
  const endpoint = `/api/pfams/${taxaId}`;
  window.location.href = endpoint;
}

function redirectToCoverageEndpoint() {
  const proteinId = document.getElementById("coverage-input").value;
  const endpoint = `/api/coverage/${proteinId}`;
  window.location.href = endpoint;
}
