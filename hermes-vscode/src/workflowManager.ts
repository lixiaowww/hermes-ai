import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';

export interface WorkflowStatus {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    currentStep: string;
    progress: number;
    startTime: Date;
    endTime?: Date;
    error?: string;
}

export class WorkflowManager {
    private currentWorkflow: WorkflowStatus | null = null;
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
        this.statusBarItem.text = "$(sync~spin) ZSCE Agent";
        this.statusBarItem.tooltip = "Click to start development workflow";
        this.statusBarItem.command = 'zswe-agent.startWorkflow';
        this.statusBarItem.show();
    }

    async startWorkflow(): Promise<void> {
        try {
            // 获取用户输入
            const userPrompt = await vscode.window.showInputBox({
                prompt: 'Enter your development task description',
                placeHolder: 'e.g., Create a simple calculator function',
                validateInput: (text) => {
                    return text.length > 0 ? null : 'Task description cannot be empty';
                }
            });

            if (!userPrompt) {
                return;
            }

            // 获取工作区路径
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }

            // 检查是否有Python环境
            const pythonPath = await this.getPythonPath();
            if (!pythonPath) {
                vscode.window.showErrorMessage('Python not found. Please install Python and activate a virtual environment.');
                return;
            }

            // 创建工作流状态
            this.currentWorkflow = {
                id: Date.now().toString(),
                status: 'running',
                currentStep: 'Starting workflow...',
                progress: 0,
                startTime: new Date()
            };

            this.updateStatusBar();
            this.showProgress();

            // 启动Python后端进程
            await this.runPythonWorkflow(workspaceFolder.uri.fsPath, userPrompt);

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start workflow: ${error}`);
            this.currentWorkflow = null;
            this.updateStatusBar();
        }
    }

    private async getPythonPath(): Promise<string | null> {
        try {
            // 尝试获取Python路径
            const pythonPath = await vscode.workspace.getConfiguration('python').get('pythonPath') as string;
            if (pythonPath) {
                return pythonPath;
            }

            // 尝试系统Python
            const result = child_process.execSync('which python3', { encoding: 'utf8' });
            return result.trim();
        } catch {
            return null;
        }
    }

    private async runPythonWorkflow(workspacePath: string, userPrompt: string): Promise<void> {
        return new Promise((resolve, reject) => {
            // 构建Python命令
            const pythonCommand = 'python3';
            const scriptPath = path.join(workspacePath, 'zswe-agent', 'zswe_agent', 'main.py');
            const args = [scriptPath, userPrompt, '--yes'];

            // 设置环境变量
            const envVars: NodeJS.ProcessEnv = { ...process.env };
            const config = vscode.workspace.getConfiguration('zsweAgent');
            if (config.get('apiKey')) {
                envVars.GOOGLE_API_KEY = config.get('apiKey') as string;
            }

            // 启动进程
            const pythonProcess = child_process.spawn(pythonCommand, args, {
                cwd: workspacePath,
                env: envVars,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            let errorOutput = '';

            pythonProcess.stdout?.on('data', (data: Buffer) => {
                output += data.toString();
                this.updateWorkflowOutput(output);
            });

            pythonProcess.stderr?.on('data', (data: Buffer) => {
                errorOutput += data.toString();
            });

            pythonProcess.on('close', (code: number) => {
                if (code === 0) {
                    this.currentWorkflow!.status = 'completed';
                    this.currentWorkflow!.progress = 100;
                    this.currentWorkflow!.endTime = new Date();
                    vscode.window.showInformationMessage('Workflow completed successfully!');
                } else {
                    this.currentWorkflow!.status = 'failed';
                    this.currentWorkflow!.error = errorOutput || 'Unknown error occurred';
                    vscode.window.showErrorMessage(`Workflow failed with code ${code}`);
                }
                this.updateStatusBar();
                resolve();
            });

            pythonProcess.on('error', (error: Error) => {
                this.currentWorkflow!.status = 'failed';
                this.currentWorkflow!.error = error.message;
                this.updateStatusBar();
                reject(error);
            });
        });
    }

    private updateWorkflowOutput(output: string): void {
        // 解析输出并更新工作流状态
        if (output.includes('Step 1:')) {
            this.currentWorkflow!.currentStep = 'Generating test case...';
            this.currentWorkflow!.progress = 25;
        } else if (output.includes('Step 2:')) {
            this.currentWorkflow!.currentStep = 'Generating initial code...';
            this.currentWorkflow!.progress = 50;
        } else if (output.includes('Debate Round')) {
            this.currentWorkflow!.currentStep = 'Agent debate in progress...';
            this.currentWorkflow!.progress = 75;
        }

        this.updateStatusBar();
    }

    private updateStatusBar(): void {
        if (!this.currentWorkflow) {
            this.statusBarItem.text = "$(sync~spin) ZSCE Agent";
            this.statusBarItem.tooltip = "Click to start development workflow";
            return;
        }

        switch (this.currentWorkflow.status) {
            case 'running':
                this.statusBarItem.text = `$(sync~spin) ZSCE Agent: ${this.currentWorkflow.currentStep}`;
                this.statusBarItem.tooltip = `Progress: ${this.currentWorkflow.progress}%`;
                break;
            case 'completed':
                this.statusBarItem.text = "$(check) ZSCE Agent: Completed";
                this.statusBarItem.tooltip = "Workflow completed successfully";
                break;
            case 'failed':
                this.statusBarItem.text = "$(error) ZSCE Agent: Failed";
                this.statusBarItem.tooltip = `Error: ${this.currentWorkflow.error}`;
                break;
        }
    }

    private showProgress(): void {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "ZSCE Agent Workflow",
            cancellable: false
        }, async (progress) => {
            while (this.currentWorkflow?.status === 'running') {
                progress.report({
                    message: this.currentWorkflow.currentStep,
                    increment: this.currentWorkflow.progress
                });
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        });
    }

    showWorkflowStatus(): void {
        if (!this.currentWorkflow) {
            vscode.window.showInformationMessage('No active workflow');
            return;
        }

        const message = `Workflow Status: ${this.currentWorkflow.status}\n` +
                       `Current Step: ${this.currentWorkflow.currentStep}\n` +
                       `Progress: ${this.currentWorkflow.progress}%\n` +
                       `Started: ${this.currentWorkflow.startTime.toLocaleTimeString()}`;

        if (this.currentWorkflow.error) {
            vscode.window.showErrorMessage(message + `\nError: ${this.currentWorkflow.error}`);
        } else {
            vscode.window.showInformationMessage(message);
        }
    }

    getCurrentWorkflow(): WorkflowStatus | null {
        return this.currentWorkflow;
    }
}
