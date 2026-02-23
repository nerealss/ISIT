namespace WorldMapCountryInfo
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.gMapControl1 = new GMap.NET.WindowsForms.GMapControl();
            this.panelInfo = new System.Windows.Forms.Panel();
            this.lblCountryName = new System.Windows.Forms.Label();
            this.picFlag = new System.Windows.Forms.PictureBox();
            this.lblCurrency = new System.Windows.Forms.Label();
            this.lblPopulation = new System.Windows.Forms.Label();
            this.btnClose = new System.Windows.Forms.Button();
            this.panelInfo.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picFlag)).BeginInit();
            this.SuspendLayout();

            // gMapControl1
            this.gMapControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.gMapControl1.Location = new System.Drawing.Point(0, 0);
            this.gMapControl1.Name = "gMapControl1";
            this.gMapControl1.Size = new System.Drawing.Size(900, 600);
            this.gMapControl1.TabIndex = 0;

            // panelInfo
            this.panelInfo.BackColor = System.Drawing.Color.White;
            this.panelInfo.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.panelInfo.Controls.Add(this.lblCountryName);
            this.panelInfo.Controls.Add(this.picFlag);
            this.panelInfo.Controls.Add(this.lblCurrency);
            this.panelInfo.Controls.Add(this.lblPopulation);
            this.panelInfo.Controls.Add(this.btnClose);
            this.panelInfo.Location = new System.Drawing.Point(25, 25);
            this.panelInfo.Name = "panelInfo";
            this.panelInfo.Size = new System.Drawing.Size(260, 330);
            this.panelInfo.Visible = false;

            // lblCountryName
            this.lblCountryName.Font = new System.Drawing.Font("Segoe UI", 16F, System.Drawing.FontStyle.Bold);
            this.lblCountryName.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.lblCountryName.Location = new System.Drawing.Point(10, 15);
            this.lblCountryName.Size = new System.Drawing.Size(240, 40);

            // picFlag
            this.picFlag.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.picFlag.Location = new System.Drawing.Point(45, 65);
            this.picFlag.Size = new System.Drawing.Size(170, 100);
            this.picFlag.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;

            // lblCurrency
            this.lblCurrency.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.lblCurrency.Location = new System.Drawing.Point(15, 185);
            this.lblCurrency.Size = new System.Drawing.Size(230, 25);

            // lblPopulation
            this.lblPopulation.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.lblPopulation.Location = new System.Drawing.Point(15, 215);
            this.lblPopulation.Size = new System.Drawing.Size(230, 25);

            // btnClose
            this.btnClose.Location = new System.Drawing.Point(85, 275);
            this.btnClose.Size = new System.Drawing.Size(90, 35);
            this.btnClose.Text = "Закрыть";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);

            // MainForm
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(900, 600);
            this.Controls.Add(this.panelInfo);
            this.Controls.Add(this.gMapControl1);
            this.Name = "MainForm";
            this.Text = "Интерактивная карта мира";
            this.panelInfo.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.picFlag)).EndInit();
            this.ResumeLayout(false);
        }

        private GMap.NET.WindowsForms.GMapControl gMapControl1;
        private System.Windows.Forms.Panel panelInfo;
        private System.Windows.Forms.Label lblCountryName;
        private System.Windows.Forms.PictureBox picFlag;
        private System.Windows.Forms.Label lblCurrency;
        private System.Windows.Forms.Label lblPopulation;
        private System.Windows.Forms.Button btnClose;
    }
}