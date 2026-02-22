# Information Security Policy

**Effective Date:** January 1, 2025
**Last Updated:** January 20, 2025
**Policy Owner:** Information Security Team

## 1. Purpose

This policy establishes the information security requirements for all Acme Corporation employees, contractors, and third-party users. Protecting company data, customer information, and intellectual property is everyone's responsibility.

## 2. Scope

This policy applies to all employees, contractors, interns, and any person granted access to Acme Corporation's information systems, data, or facilities.

## 3. Password Requirements

### 3.1 Password Standards

- Minimum 12 characters in length
- Must include at least one uppercase letter, one lowercase letter, one number, and one special character
- Passwords must be changed every 90 days
- Cannot reuse any of the last 10 passwords
- Must not contain the employee's name, username, or common dictionary words

### 3.2 Multi-Factor Authentication (MFA)

MFA is mandatory for:
- All company email accounts
- VPN access
- Cloud service accounts (AWS, GCP, etc.)
- HR and financial systems
- Code repositories

Employees must register at least two MFA methods (e.g., authenticator app and phone number). Hardware security keys are available upon request from IT.

## 4. Data Classification

### 4.1 Classification Levels

| Level | Description | Examples |
|-------|-------------|----------|
| Public | Information approved for public release | Marketing materials, job postings |
| Internal | General business information | Internal memos, org charts |
| Confidential | Sensitive business data | Financial reports, strategy docs, customer lists |
| Restricted | Highly sensitive data | PII, payment data, trade secrets, source code |

### 4.2 Handling Requirements

- **Public:** No special handling required.
- **Internal:** Do not share outside the company. Use company email only.
- **Confidential:** Encrypt in transit and at rest. Share only on a need-to-know basis. Label documents as "Confidential."
- **Restricted:** Encrypt at all times. Access requires manager and security team approval. Log all access. Cannot be stored on personal devices.

## 5. Acceptable Use

### 5.1 Company Devices

Company-issued devices are primarily for business use. Limited personal use is permitted but must not interfere with work duties. All company devices are subject to monitoring. Employees must not install unauthorized software on company devices.

### 5.2 Email Security

- Do not open attachments from unknown senders
- Report phishing emails to security@acmecorp.com
- Do not use personal email for business communications
- Do not auto-forward company email to personal accounts
- Encrypt emails containing Confidential or Restricted data

### 5.3 Internet Usage

- Do not visit malicious or inappropriate websites on company devices
- Do not download unauthorized software or files
- Streaming media for personal use should be limited and not affect network performance

## 6. Incident Response

### 6.1 Reporting

All security incidents must be reported immediately to the Security Operations Center (SOC) at:
- Email: security@acmecorp.com
- Phone: ext. 9111
- Slack: #security-incidents

### 6.2 Types of Incidents

Reportable incidents include:
- Lost or stolen devices
- Suspected phishing or social engineering attempts
- Unauthorized access to systems or data
- Malware infections
- Data breaches or leaks
- Physical security breaches

### 6.3 Response Process

1. Report the incident immediately
2. Preserve evidence (do not delete files or logs)
3. Follow instructions from the SOC team
4. Document what happened and when
5. Cooperate with any investigation

## 7. Physical Security

- Always wear your badge visibly in the office
- Do not tailgate through secure doors
- Lock your workstation when leaving your desk (Windows: Win+L, Mac: Ctrl+Cmd+Q)
- Report lost badges immediately to facilities@acmecorp.com
- Visitors must sign in at reception and be escorted at all times
- Do not leave sensitive documents on desks overnight (clean desk policy)

## 8. Third-Party Access

Third-party vendors requiring system access must:
- Sign a Non-Disclosure Agreement (NDA)
- Complete a security assessment
- Use time-limited credentials
- Access only the minimum systems necessary
- Be sponsored by an internal employee

## 9. Security Training

All employees must complete:
- Annual security awareness training (due by March 31 each year)
- Phishing simulation exercises (quarterly)
- Role-specific security training (for engineering, finance, and HR roles)

Failure to complete mandatory training within 30 days of the deadline may result in restricted system access.

## 10. Violations

Violations of this security policy may result in:
- Verbal or written warning
- Restricted system access
- Mandatory additional training
- Suspension or termination
- Legal action in cases of intentional data theft or sabotage

## 11. Contact

For security questions or to report incidents, contact the Security Team at security@acmecorp.com or ext. 9111.
