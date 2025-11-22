const API_BASE = 'http://localhost:8000/api';

// Tab Management
function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');

    if (tabName === 'patients') loadPatients();
    else if (tabName === 'transfers') loadTransfers();
    else if (tabName === 'hospitals') loadHospitals();
}

// Load Patients
async function loadPatients() {
    const hospitalId = document.getElementById('hospitalFilter').value;
    const triageLevel = document.getElementById('triageFilter').value;

    let url = `${API_BASE}/patients/?limit=100`;
    if (hospitalId) url += `&hospital_id=${hospitalId}`;
    if (triageLevel) url += `&triage_level=${triageLevel}`;

    try {
        const res = await fetch(url);
        const patients = await res.json();

        const list = document.getElementById('patientsList');
        list.innerHTML = `
            <div class="table-row header">
                <div>MRN</div>
                <div>Name</div>
                <div>Triage</div>
                <div>Hospital ID</div>
                <div>Admission Date</div>
            </div>
        `;

        patients.forEach(p => {
            const row = document.createElement('div');
            row.className = 'table-row';
            row.innerHTML = `
                <div>${p.mrn}</div>
                <div>${p.first_name} ${p.last_name}</div>
                <div><span class="badge ${p.triage_level}">${p.triage_level || 'N/A'}</span></div>
                <div>${p.hospital_id}</div>
                <div>${new Date(p.admission_date).toLocaleDateString()}</div>
            `;
            list.appendChild(row);
        });

        if (patients.length === 0) {
            list.innerHTML += '<div class="loading">No patients found</div>';
        }
    } catch (err) {
        console.error('Error loading patients:', err);
        document.getElementById('patientsList').innerHTML =
            '<div class="error">Error loading patients. Make sure the backend server is running.</div>';
    }
}

// Load Transfers
async function loadTransfers() {
    const status = document.getElementById('transferStatusFilter').value;
    let url = `${API_BASE}/transfers/`;
    if (status) url += `?status=${status}`;

    try {
        const res = await fetch(url);
        const transfers = await res.json();

        const list = document.getElementById('transfersList');
        list.innerHTML = `
            <div class="table-row header">
                <div>Transfer ID</div>
                <div>Patient ID</div>
                <div>From Hospital</div>
                <div>To Hospital</div>
                <div>Status</div>
                <div>Priority</div>
            </div>
        `;

        transfers.forEach(t => {
            const row = document.createElement('div');
            row.className = 'table-row';
            row.innerHTML = `
                <div>#${t.id}</div>
                <div>${t.patient_id}</div>
                <div>Hospital ${t.from_hospital_id}</div>
                <div>Hospital ${t.to_hospital_id}</div>
                <div><span class="badge ${t.transfer_status}">${t.transfer_status}</span></div>
                <div><span class="badge ${t.priority}">${t.priority || 'N/A'}</span></div>
            `;
            list.appendChild(row);
        });

        if (transfers.length === 0) {
            list.innerHTML += '<div class="loading">No transfers found</div>';
        }
    } catch (err) {
        console.error('Error loading transfers:', err);
        document.getElementById('transfersList').innerHTML =
            '<div class="error">Error loading transfers. Make sure the backend server is running.</div>';
    }
}

// Load Hospitals
async function loadHospitals() {
    try {
        const res = await fetch(`${API_BASE}/hospitals/`);
        const hospitals = await res.json();

        const list = document.getElementById('hospitalsList');
        list.innerHTML = `
            <div class="table-row header">
                <div>ID</div>
                <div>Name</div>
                <div>City</div>
                <div>Capacity</div>
                <div>Available Beds</div>
                <div>Occupancy</div>
            </div>
        `;

        hospitals.forEach(h => {
            const occupancy = ((h.capacity - h.available_beds) / h.capacity * 100).toFixed(1);
            const row = document.createElement('div');
            row.className = 'table-row';
            row.innerHTML = `
                <div>${h.id}</div>
                <div><strong>${h.name}</strong></div>
                <div>${h.city}, ${h.state}</div>
                <div>${h.capacity}</div>
                <div>${h.available_beds}</div>
                <div>${occupancy}%</div>
            `;
            list.appendChild(row);
        });

        // Update hospital filter
        const filter = document.getElementById('hospitalFilter');
        filter.innerHTML = '<option value="">All Hospitals</option>';
        hospitals.forEach(h => {
            filter.innerHTML += `<option value="${h.id}">${h.name}</option>`;
        });

        if (hospitals.length === 0) {
            list.innerHTML += '<div class="loading">No hospitals found</div>';
        }
    } catch (err) {
        console.error('Error loading hospitals:', err);
        document.getElementById('hospitalsList').innerHTML =
            '<div class="error">Error loading hospitals. Make sure the backend server is running.</div>';
    }
}

// Modal functions (simplified - expand as needed)
function showAddPatientModal() {
    alert('Add Patient functionality - You can expand this with a full form modal');
}

function showAddTransferModal() {
    alert('Add Transfer functionality - You can expand this with a full form modal');
}

function showAddHospitalModal() {
    alert('Add Hospital functionality - You can expand this with a full form modal');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
    loadHospitals();
});