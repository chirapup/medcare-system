const API_BASE = 'http://localhost:8000/api';

// System time update
function updateSystemTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    document.getElementById('systemTime').textContent = timeStr;
}
setInterval(updateSystemTime, 1000);
updateSystemTime();

// Sidebar navigation
document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('click', function() {
        const view = this.dataset.view;

        // Update active sidebar item
        document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');

        // Show selected view
        document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active'));
        document.getElementById(`${view}-view`).classList.add('active');

        // Load data for the view
        if (view === 'patients') loadPatients();
        else if (view === 'transfers') loadTransfers();
        else if (view === 'hospitals') loadHospitals();
        else if (view === 'capacity') loadCapacity();
        else if (view === 'analytics') loadAnalytics();
    });
});

// Calculate age from date of birth
function calculateAge(dob) {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

// Format date for display
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric'
    });
}

// Format datetime for display
function formatDateTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Load Patients
async function loadPatients() {
    const hospitalId = document.getElementById('patientHospitalFilter').value;
    const triageLevel = document.getElementById('patientTriageFilter').value;

    let url = `${API_BASE}/patients/?limit=100`;
    if (hospitalId) url += `&hospital_id=${hospitalId}`;
    if (triageLevel) url += `&triage_level=${triageLevel}`;

    try {
        const res = await fetch(url);
        const patients = await res.json();

        const tbody = document.getElementById('patientsTableBody');
        tbody.innerHTML = '';

        if (patients.length === 0) {
            tbody.innerHTML = '<tr class="loading-row"><td colspan="7">No patients found</td></tr>';
            document.getElementById('patientCount').textContent = '0 patients';
            return;
        }

        // Update count
        document.getElementById('patientCount').textContent = `${patients.length} patients`;

        patients.forEach(p => {
            const dob = formatDate(p.date_of_birth);
            const age = calculateAge(p.date_of_birth);
            const triageClass = p.triage_level ? p.triage_level.toLowerCase() : 'non_urgent';
            const triageText = p.triage_level ? p.triage_level.replace('_', '-') : 'N/A';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${p.mrn}</strong></td>
                <td>${p.last_name}, ${p.first_name}</td>
                <td>${dob}<br><span style="color:#6b7280;font-size:12px;">${age} years</span></td>
                <td><span class="triage-badge triage-${triageClass}">${triageText}</span></td>
                <td>Facility ${p.hospital_id}</td>
                <td>${formatDateTime(p.admission_date)}</td>
                <td><span class="status-badge status-active">Active</span></td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error('Error loading patients:', err);
        document.getElementById('patientsTableBody').innerHTML =
            '<tr class="loading-row"><td colspan="7" style="color:#d32f2f;">Error loading data. Check console.</td></tr>';
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

        const tbody = document.getElementById('transfersTableBody');
        tbody.innerHTML = '';

        if (transfers.length === 0) {
            tbody.innerHTML = '<tr class="loading-row"><td colspan="8">No transfers found</td></tr>';
            document.getElementById('transferCount').textContent = '0 transfers';
            return;
        }

        document.getElementById('transferCount').textContent = `${transfers.length} transfers`;

        transfers.forEach(t => {
            const statusClass = t.transfer_status.toLowerCase();
            const priorityClass = t.priority ? t.priority.toLowerCase() : 'non_urgent';
            const priorityText = t.priority ? t.priority.replace('_', '-') : 'Standard';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>T${String(t.id).padStart(6, '0')}</strong></td>
                <td>Patient #${t.patient_id}</td>
                <td>Facility ${t.from_hospital_id}</td>
                <td>Facility ${t.to_hospital_id}</td>
                <td><span class="triage-badge triage-${priorityClass}">${priorityText}</span></td>
                <td><span class="status-badge status-${statusClass}">${t.transfer_status.replace('_', ' ')}</span></td>
                <td>${formatDateTime(t.requested_at)}</td>
                <td><button class="btn-secondary" style="padding:6px 12px;font-size:12px;">View</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error('Error loading transfers:', err);
        document.getElementById('transfersTableBody').innerHTML =
            '<tr class="loading-row"><td colspan="8" style="color:#d32f2f;">Error loading data.</td></tr>';
    }
}

// Load Hospitals
async function loadHospitals() {
    try {
        const res = await fetch(`${API_BASE}/hospitals/`);
        const hospitals = await res.json();

        const tbody = document.getElementById('hospitalsTableBody');
        tbody.innerHTML = '';

        if (hospitals.length === 0) {
            tbody.innerHTML = '<tr class="loading-row"><td colspan="7">No facilities found</td></tr>';
            document.getElementById('hospitalCount').textContent = '0 facilities';
            return;
        }

        document.getElementById('hospitalCount').textContent = `${hospitals.length} facilities`;

        hospitals.forEach(h => {
            const occupancy = ((h.capacity - h.available_beds) / h.capacity * 100).toFixed(0);
            const statusText = h.available_beds > 10 ? 'Available' : h.available_beds > 0 ? 'Limited' : 'Full';
            const statusClass = h.available_beds > 10 ? 'active' : h.available_beds > 0 ? 'pending' : 'cancelled';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>F${String(h.id).padStart(4, '0')}</strong></td>
                <td><strong>${h.name}</strong></td>
                <td>${h.city}, ${h.state}</td>
                <td>${h.capacity}</td>
                <td><strong>${h.available_beds}</strong></td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="flex:1;height:6px;background:#e5e7eb;border-radius:3px;">
                            <div style="height:100%;width:${occupancy}%;background:${occupancy > 90 ? '#d32f2f' : occupancy > 70 ? '#ff8c00' : '#00a651'};border-radius:3px;"></div>
                        </div>
                        <span style="font-weight:600;min-width:45px;">${occupancy}%</span>
                    </div>
                </td>
                <td><span class="status-badge status-${statusClass}">${statusText}</span></td>
            `;
            tbody.appendChild(row);
        });

        // Update filter dropdowns
        const filter = document.getElementById('patientHospitalFilter');
        filter.innerHTML = '<option value="">All Facilities</option>';
        hospitals.forEach(h => {
            filter.innerHTML += `<option value="${h.id}">${h.name}</option>`;
        });
    } catch (err) {
        console.error('Error loading hospitals:', err);
        document.getElementById('hospitalsTableBody').innerHTML =
            '<tr class="loading-row"><td colspan="7" style="color:#d32f2f;">Error loading data.</td></tr>';
    }
}

// Load Capacity View
async function loadCapacity() {
    try {
        const res = await fetch(`${API_BASE}/hospitals/`);
        const hospitals = await res.json();

        const grid = document.getElementById('capacityGrid');
        grid.innerHTML = '';

        hospitals.forEach(h => {
            const occupancy = ((h.capacity - h.available_beds) / h.capacity * 100).toFixed(0);
            const fillClass = occupancy > 90 ? 'high' : occupancy > 70 ? 'medium' : 'low';

            const card = document.createElement('div');
            card.className = 'capacity-card';
            card.innerHTML = `
                <h3>${h.name}</h3>
                <div class="capacity-bar">
                    <div class="capacity-fill ${fillClass}" style="width:${occupancy}%"></div>
                </div>
                <div class="capacity-stats">
                    <div>
                        <div class="capacity-label">Total Beds</div>
                        <div class="capacity-value">${h.capacity}</div>
                    </div>
                    <div>
                        <div class="capacity-label">Available</div>
                        <div class="capacity-value">${h.available_beds}</div>
                    </div>
                    <div>
                        <div class="capacity-label">Occupancy</div>
                        <div class="capacity-value">${occupancy}%</div>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error('Error loading capacity:', err);
    }
}

// Load Analytics
async function loadAnalytics() {
    try {
        const [patientsRes, transfersRes, hospitalsRes] = await Promise.all([
            fetch(`${API_BASE}/patients/?limit=1000`),
            fetch(`${API_BASE}/transfers/`),
            fetch(`${API_BASE}/hospitals/`)
        ]);

        const patients = await patientsRes.json();
        const transfers = await transfersRes.json();
        const hospitals = await hospitalsRes.json();

        // Calculate stats
        const totalPatients = patients.length;
        const activeTransfers = transfers.filter(t => t.transfer_status === 'PENDING' || t.transfer_status === 'IN_PROGRESS').length;
        const totalCapacity = hospitals.reduce((sum, h) => sum + h.capacity, 0);
        const totalAvailable = hospitals.reduce((sum, h) => sum + h.available_beds, 0);
        const networkCapacity = ((totalCapacity - totalAvailable) / totalCapacity * 100).toFixed(0);
        const criticalPatients = patients.filter(p => p.triage_level === 'CRITICAL').length;

        document.getElementById('totalPatients').textContent = totalPatients;
        document.getElementById('activeTransfers').textContent = activeTransfers;
        document.getElementById('networkCapacity').textContent = `${networkCapacity}%`;
        document.getElementById('criticalPatients').textContent = criticalPatients;
    } catch (err) {
        console.error('Error loading analytics:', err);
    }
}

// Refresh functions
function refreshPatients() {
    loadPatients();
}

function refreshTransfers() {
    loadTransfers();
}

function refreshHospitals() {
    loadHospitals();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
    loadHospitals();
});