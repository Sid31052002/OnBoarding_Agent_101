import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import {
  Container, Typography, TextField, Button, LinearProgress, Box, Paper, Stepper, Step, StepLabel, Accordion, AccordionSummary, AccordionDetails
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";
const DOCUMENT_SEQUENCE = [
  "commercial_license",
  "eid_resident_card",
  "trade_license"
];

export default function DashboardPage() {
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchProgress = async () => {
    if (!email) {
      setError("Please enter your email.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${BASE_URL}/progress/${email}`);
      if (res.ok) {
        const data = await res.json();
        setProgress(data);
      } else {
        setError("Could not fetch progress. Please check your email and try again.");
        setProgress(null);
      }
    } catch (err) {
      setError("Error: " + err.message);
      setProgress(null);
    }
    setLoading(false);
  };

  // Calculate step index
  let stepIdx = 0;
  if (progress) {
    if (progress.current_step === "ask_account_open") stepIdx = 0;
    else if (progress.current_step === "completed") stepIdx = DOCUMENT_SEQUENCE.length;
    else {
      const idx = DOCUMENT_SEQUENCE.indexOf(progress.current_step);
      stepIdx = idx >= 0 ? idx + 1 : 0;
    }
  }

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          📊 Onboarding Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <TextField
            label="Enter your registered email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            fullWidth
          />
          <Button variant="contained" onClick={fetchProgress} disabled={loading}>
            Check Progress
          </Button>
        </Box>
        {error && <Typography color="error">{error}</Typography>}
        {progress && (
          <>
            <Typography variant="h6" gutterBottom>
              Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(stepIdx / DOCUMENT_SEQUENCE.length) * 100}
              sx={{ height: 10, borderRadius: 5, mb: 2 }}
            />
            <Stepper activeStep={stepIdx} alternativeLabel>
              {DOCUMENT_SEQUENCE.map((step, idx) => {
                const stepName = step.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                let status = progress.documents?.[step]?.status || "pending";
                let label = stepName;
                if (progress.current_step === "completed" || status === "validated") label += " ✅";
                else if (progress.current_step === step) label += " (In Progress)";
                else if (status === "pending_confirmation") label += " (Awaiting Confirmation)";
                else if (status === "awaiting_upload") label += " (Awaiting Upload)";
                return (
                  <Step key={step}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                );
              })}
            </Stepper>
            <Typography variant="h6" sx={{ mt: 3 }}>
              Document Details
            </Typography>
            {progress.documents && Object.entries(progress.documents).length > 0 ? (
              Object.entries(progress.documents).map(([doc, info]) => (
                <Accordion key={doc}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>
                      {doc.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())} Details
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography><b>Status:</b> {info.status || "pending"}</Typography>
                    {info.file && <Typography><b>File:</b> {info.file}</Typography>}
                    {info.data && (
                      <Box mt={1}>
                        <Typography variant="subtitle2">Extracted Data:</Typography>
                        <pre style={{ background: "#f5f5f5", padding: 8, borderRadius: 4 }}>
                          {formatExtractedData(info.data)}
                        </pre>
                      </Box>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))
            ) : (
              <Typography>No documents uploaded yet.</Typography>
            )}
            {progress.current_step === "completed" && (
              <Typography color="success.main" variant="h5" align="center" sx={{ mt: 2 }}>
                🎉 Onboarding Completed!
              </Typography>
            )}
          </>
        )}
      </Paper>
    </Container>
  );
}

// Add this helper function at the top or bottom of your file:
function formatExtractedData(data) {
  try {
    const obj = typeof data === "string" ? JSON.parse(data) : data;
    if (typeof obj === "object" && obj !== null) {
      return Object.entries(obj)
        .map(([key, value]) => `${key}: ${value}`)
        .join("\n");
    }
    return data;
  } catch {
    return data;
  }
}