import React, { useEffect, useState } from "react";
import { Container, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress } from "@mui/material";

const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";

// Add your document sequence here (should match backend)
const DOCUMENT_SEQUENCE = [
  "commercial_license",
  "eid_resident_card",
  "trade_license"
];

export default function AdminDashboardPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch all registered users and their progress
    async function fetchUsers() {
      try {
        const res = await fetch(`${BASE_URL}/all_users_progress`);
        if (res.ok) {
          const data = await res.json();
          setUsers(data);
        }
      } catch (err) {
        setUsers([]);
      }
      setLoading(false);
    }
    fetchUsers();
  }, []);

  // Helper to get the latest document name
  function getLatestDocumentName(documents) {
    if (!documents || Object.keys(documents).length === 0) return "N/A";
    // Get the last key in the documents object (assuming insertion order is preserved)
    const docNames = Object.keys(documents);
    return docNames[docNames.length - 1];
  }

  function getStatus(progress) {
    if (!progress || !progress.current_step) return "Yet to Start";
    if (progress.current_step === "completed") return "Completed";
    if (progress.current_step === "ask_account_open") return "Yet to Start";
    return "In Progress";
  }

  function getCurrentStepDisplay(progress) {
    if (!progress || !progress.current_step) return "N/A";
    if (progress.current_step === "completed") return "Completed";
    if (progress.current_step === "ask_account_open") return "Yet to Start";
    const idx = DOCUMENT_SEQUENCE.indexOf(progress.current_step);
    if (idx === -1) return progress.current_step;
    // Format: Document Name (n/total)
    const docName = progress.current_step.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
    return `${docName} (${idx + 1}/${DOCUMENT_SEQUENCE.length})`;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          🛡️ Admin Dashboard
        </Typography>
        {loading ? (
          <CircularProgress />
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Business Name</TableCell>
                  <TableCell>Current Step</TableCell>
                  <TableCell>Latest Document</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.email}>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.business_name}</TableCell>
                    <TableCell>
                      {getCurrentStepDisplay(user.progress)}
                    </TableCell>
                    <TableCell>
                      {user.progress?.documents
                        ? getLatestDocumentName(user.progress.documents)
                        : "N/A"}
                    </TableCell>
                    <TableCell>
                      {getStatus(user.progress)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Container>
  );
}
