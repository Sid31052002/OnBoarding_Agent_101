import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Container, TextField, Button, Typography, Box, Paper } from "@mui/material";

const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";
const SUBMISSION_END_POINT = process.env.REACT_APP_SUBMISSION_END_POINT || "/register_customer";

export default function RegisterPage() {
  const [form, setForm] = useState({ name: "", email: "", phone: "", business_name: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { name, email, phone, business_name } = form;
    if (!/^\d{10}$/.test(phone) || parseInt(phone, 10) < 6000000000) {
      setError("Please enter a valid 10-digit Indian mobile number.");
      return;
    }
    try {
      const res = await fetch(`${BASE_URL}${SUBMISSION_END_POINT}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, phone: parseInt(phone, 10), business_name }),
      });
      if (res.ok) {
        setSuccess("Registration successful! Please check your email for next steps.");
        setTimeout(() => navigate("/dashboard", { state: { email } }), 1000);
      } else {
        setError("Registration failed. Please try again.");
      }
    } catch (err) {
      setError("Error: " + err.message);
    }
  };

  const handleCheckProgress = () => {
    navigate("/dashboard");
  };

  const handleAdminPortal = () => {
    navigate("/admin");
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          🏦 Customer Onboarding
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Full Name"
            name="name"
            value={form.name}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
          />
          <TextField
            label="Email"
            name="email"
            value={form.email}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
            type="email"
          />
          <TextField
            label="Phone Number"
            name="phone"
            value={form.phone}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
            inputProps={{ maxLength: 10 }}
          />
          <TextField
            label="Business Name"
            name="business_name"
            value={form.business_name}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
          />
          {error && <Typography color="error">{error}</Typography>}
          {success && <Typography color="primary">{success}</Typography>}
          <Box mt={2}>
            <Button type="submit" variant="contained" color="primary" fullWidth>
              Register
            </Button>
          </Box>
        </form>
        <Box mt={2} textAlign="center">
          <Typography variant="body2">
            Already registered?
            <Button variant="text" onClick={handleCheckProgress}>
              Check Progress
            </Button>
          </Typography>
          <Button variant="outlined" color="secondary" onClick={handleAdminPortal} sx={{ mt: 2 }}>
            Admin Portal
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}