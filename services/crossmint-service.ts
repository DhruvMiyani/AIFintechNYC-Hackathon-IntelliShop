#!/usr/bin/env tsx
/**
 * Crossmint Wallet Integration Service
 * Provides crypto wallet functionality as alternative payment processor
 */

import { CrossmintWallets, createCrossmint, Wallet } from "@crossmint/wallets-sdk";

export interface CrossmintConfig {
  apiKey: string;
  jwt?: string;
  environment?: 'staging' | 'production';
}

export interface CrossmintPaymentRequest {
  amount: string;
  currency: string; // 'usdc', 'sol', 'eth', etc.
  recipient: string; // wallet address or email
  chain: string; // 'solana', 'ethereum', 'polygon', etc.
  senderEmail: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface CrossmintPaymentResult {
  success: boolean;
  transactionId?: string;
  explorerLink?: string;
  walletAddress?: string;
  error?: string;
  processingTime: number;
  fees?: {
    networkFee: string;
    serviceFee: string;
    total: string;
  };
}

export class CrossmintWalletService {
  private crossmint: any;
  private crossmintWallets: any;
  private config: CrossmintConfig;

  constructor(config: CrossmintConfig) {
    this.config = config;
    this.crossmint = createCrossmint({
      apiKey: config.apiKey,
      jwt: config.jwt,
    });
    this.crossmintWallets = CrossmintWallets.from(this.crossmint);
  }

  /**
   * Process payment through Crossmint wallet
   */
  async processPayment(request: CrossmintPaymentRequest): Promise<CrossmintPaymentResult> {
    const startTime = Date.now();
    
    try {
      console.log(`🌐 Processing Crossmint payment: ${request.amount} ${request.currency.toUpperCase()}`);

      // Get or create sender wallet
      const senderWallet = await this.getOrCreateWallet(request.senderEmail, request.chain);
      
      // Check balance
      const balances = await senderWallet.balances();
      const requiredBalance = parseFloat(request.amount);
      
      let currentBalance = 0;
      if (request.currency.toLowerCase() === 'usdc') {
        currentBalance = parseFloat(balances.usdc?.amount || '0');
      } else if (request.currency.toLowerCase() === 'sol' || request.currency.toLowerCase() === 'eth') {
        currentBalance = parseFloat(balances.nativeToken?.amount || '0');
      }

      if (currentBalance < requiredBalance) {
        return {
          success: false,
          error: `Insufficient balance. Required: ${request.amount} ${request.currency.toUpperCase()}, Available: ${currentBalance}`,
          processingTime: Date.now() - startTime
        };
      }

      // Send payment
      const transaction = await senderWallet.send(
        request.recipient,
        request.currency,
        request.amount
      );

      return {
        success: true,
        transactionId: transaction.id || transaction.hash,
        explorerLink: transaction.explorerLink,
        walletAddress: senderWallet.address,
        processingTime: Date.now() - startTime,
        fees: {
          networkFee: transaction.networkFee || '0',
          serviceFee: transaction.serviceFee || '0',
          total: transaction.totalFee || '0'
        }
      };

    } catch (error) {
      console.error('Crossmint payment error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown Crossmint error',
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Get or create wallet for user
   */
  async getOrCreateWallet(email: string, chain: string): Promise<any> {
    try {
      const wallet = await this.crossmintWallets.getOrCreateWallet({
        chain: chain,
        signer: {
          type: "email",
          email: email,
        },
      });

      console.log(`💳 Crossmint wallet: ${wallet.address} (${chain})`);
      return wallet;
    } catch (error) {
      console.error('Failed to get/create Crossmint wallet:', error);
      throw error;
    }
  }

  /**
   * Get wallet balances
   */
  async getWalletBalances(email: string, chain: string) {
    try {
      const wallet = await this.getOrCreateWallet(email, chain);
      const balances = await wallet.balances();
      
      return {
        nativeToken: {
          symbol: chain === 'solana' ? 'SOL' : 'ETH',
          amount: balances.nativeToken?.amount || '0',
          decimals: balances.nativeToken?.decimals || 9
        },
        usdc: {
          symbol: 'USDC',
          amount: balances.usdc?.amount || '0',
          decimals: balances.usdc?.decimals || 6
        }
      };
    } catch (error) {
      console.error('Failed to get wallet balances:', error);
      throw error;
    }
  }

  /**
   * Get wallet transaction history
   */
  async getWalletActivity(email: string, chain: string) {
    try {
      const wallet = await this.getOrCreateWallet(email, chain);
      const activity = await wallet.experimental_activity();
      
      return {
        events: activity.events || [],
        totalCount: activity.totalCount || 0
      };
    } catch (error) {
      console.error('Failed to get wallet activity:', error);
      return { events: [], totalCount: 0 };
    }
  }

  /**
   * Transfer tokens between wallets
   */
  async transferTokens(
    fromEmail: string,
    toAddress: string,
    amount: string,
    currency: string,
    chain: string
  ): Promise<CrossmintPaymentResult> {
    const startTime = Date.now();

    try {
      const senderWallet = await this.getOrCreateWallet(fromEmail, chain);
      
      const transaction = await senderWallet.send(toAddress, currency, amount);
      
      return {
        success: true,
        transactionId: transaction.id || transaction.hash,
        explorerLink: transaction.explorerLink,
        walletAddress: senderWallet.address,
        processingTime: Date.now() - startTime
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Transfer failed',
        processingTime: Date.now() - startTime
      };
    }
  }

  /**
   * Add delegated signer to wallet
   */
  async addDelegatedSigner(email: string, chain: string, signerAddress: string) {
    try {
      const wallet = await this.getOrCreateWallet(email, chain);
      await wallet.addDelegatedSigner({ signer: signerAddress });
      
      return { success: true };
    } catch (error) {
      console.error('Failed to add delegated signer:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to add signer' 
      };
    }
  }

  /**
   * Get delegated signers for wallet
   */
  async getDelegatedSigners(email: string, chain: string) {
    try {
      const wallet = await this.getOrCreateWallet(email, chain);
      const signers = await wallet.delegatedSigners();
      
      return { success: true, signers };
    } catch (error) {
      console.error('Failed to get delegated signers:', error);
      return { 
        success: false, 
        signers: [],
        error: error instanceof Error ? error.message : 'Failed to get signers'
      };
    }
  }

  /**
   * Validate Crossmint configuration
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.config.apiKey) {
      errors.push('Crossmint API key is required');
    }

    if (!this.config.apiKey.startsWith('sk_') && !this.config.apiKey.startsWith('pk_')) {
      errors.push('Invalid Crossmint API key format');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Get supported chains and currencies
   */
  getSupportedOptions() {
    return {
      chains: ['solana', 'ethereum', 'polygon'],
      currencies: {
        solana: ['sol', 'usdc'],
        ethereum: ['eth', 'usdc'],
        polygon: ['matic', 'usdc']
      },
      features: [
        'Wallet creation and management',
        'Token transfers (USDC, SOL, ETH, MATIC)',
        'Balance checking',
        'Transaction history',
        'Delegated signers',
        'Cross-chain support',
        'Email-based wallet access'
      ]
    };
  }
}

// Example usage and testing
export async function testCrossmintIntegration() {
  // This would use environment variables in production
  const config: CrossmintConfig = {
    apiKey: process.env.CROSSMINT_API_KEY || 'demo-api-key',
    jwt: process.env.CROSSMINT_JWT,
    environment: 'staging'
  };

  const crossmintService = new CrossmintWalletService(config);

  console.log('🧪 Testing Crossmint Wallet Integration');
  console.log('=======================================');

  // Test configuration
  const configValidation = crossmintService.validateConfig();
  console.log('Config validation:', configValidation);

  // Show supported options
  const supportedOptions = crossmintService.getSupportedOptions();
  console.log('Supported options:', supportedOptions);

  // Test wallet creation (would need real API key)
  try {
    const testEmail = 'test@example.com';
    const testChain = 'solana';

    console.log(`\n💳 Creating wallet for ${testEmail} on ${testChain}...`);
    // const balances = await crossmintService.getWalletBalances(testEmail, testChain);
    // console.log('Wallet balances:', balances);

    console.log('✅ Crossmint integration ready (requires API key for full testing)');

  } catch (error) {
    console.log('⚠️ Full testing requires valid Crossmint API key');
  }
}

if (require.main === module) {
  testCrossmintIntegration();
}