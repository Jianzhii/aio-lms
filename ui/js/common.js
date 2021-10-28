function logout() {
    sessionStorage.clear();
    window.location.href = '../../index.html';
}

function adminHome() {
    window.location.href = '../admin/admin_home.html';
}

function trainerHome() {
    window.location.href = '../trainer/trainer_home.html';
}

function learnerHome() {
    window.location.href = '../learner/learner_home.html';
}