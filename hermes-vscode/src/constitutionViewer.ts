import * as vscode from 'vscode';
import * as path from 'path';

export class ConstitutionViewer {
    async openConstitution(): Promise<void> {
        try {
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

            // 运行Python命令生成宪法
            const constitution = await this.generateConstitution(workspaceFolder.uri.fsPath);
            
            // 创建并显示宪法文档
            const document = await vscode.workspace.openTextDocument({
                content: constitution,
                language: 'markdown'
            });

            await vscode.window.showTextDocument(document, { preview: false });

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open constitution: ${error}`);
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
            const { execSync } = require('child_process');
            const result = execSync('which python3', { encoding: 'utf8' });
            return result.trim();
        } catch {
            return null;
        }
    }

    private async generateConstitution(workspacePath: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const { spawn } = require('child_process');
            
            // 构建Python命令
            const pythonCommand = 'python3';
            const scriptPath = path.join(workspacePath, 'zswe-agent', 'zswe_agent', 'constitution.py');
            
            // 创建临时Python脚本
            const tempScript = `
import sys
sys.path.append('${workspacePath}/zswe-agent')
from zswe_agent.constitution import ConstitutionGenerator

generator = ConstitutionGenerator('${workspacePath}')
constitution = generator.generate()
print(constitution)
            `;

            // 启动进程
            const process = spawn(pythonCommand, ['-c', tempScript], {
                cwd: workspacePath,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let output = '';
            let errorOutput = '';

            process.stdout?.on('data', (data: Buffer) => {
                output += data.toString();
            });

            process.stderr?.on('data', (data: Buffer) => {
                errorOutput += data.toString();
            });

            process.on('close', (code: number) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`Failed to generate constitution: ${errorOutput}`));
                }
            });

            process.on('error', (error: Error) => {
                reject(error);
            });
        });
    }
}
