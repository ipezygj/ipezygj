# XDB Chain Gateway V2.1 Connector

## Overview
This connector provides a high-performance bridge between the **Hummingbot Gateway V2.1** standard and the **XDB Chain** (EVM). It is engineered for institutional-grade liquidity provision and high-frequency trading.

## Key Technical Features
- **V2.1 Modular Architecture**: Decoupled authentication, constants, and derivative logic for maximum maintainability.
- **EVM-Native Execution**: Fully compatible with XDB Chain's JSON-RPC, ensuring minimal latency in transaction signing and broadcasting.
- **Resilient Connectivity**: Built-in health-check mechanisms to monitor network latency and handle automatic reconnections.
- **Security First**: Utilizes isolated signing via `auth.py`, ensuring sensitive keys never leave the local environment.

## File Structure
- `auth.py`: Secure EIP-155 transaction signing.
- `constants.py`: Centralized network configuration (Chain ID 111, RPC endpoints).
- `derivative.py`: Core execution engine and liquidity monitoring.

## Status: PRODUCTION READY
This connector has passed all internal **Consistency Utils** quality gates and is compliant with PEP8 and Black formatting standards.
